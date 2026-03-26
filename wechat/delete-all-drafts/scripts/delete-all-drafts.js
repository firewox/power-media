#!/usr/bin/env node
/**
 * 批量删除微信公众号草稿箱所有文章
 */

// 依赖检查
let axios;

try {
  axios = require('axios');
} catch (e) {
  console.error('缺少依赖包，请先安装：npm install axios');
  process.exit(1);
}

const WECHAT_API_BASE = 'https://api.weixin.qq.com';

// 加载配置
function loadConfig() {
  const appId = process.env.WECHAT_APP_ID;
  const appSecret = process.env.WECHAT_APP_SECRET;

  if (!appId || !appSecret) {
    throw new Error(
      '未找到微信公众号配置。请设置环境变量：\n' +
      '  WECHAT_APP_ID=your-app-id\n' +
      '  WECHAT_APP_SECRET=your-app-secret'
    );
  }

  return { appId, appSecret };
}

// Token 管理器
class AccessTokenManager {
  constructor(appId, appSecret) {
    this.appId = appId;
    this.appSecret = appSecret;
    this.accessToken = '';
    this.tokenExpireTime = 0;
  }

  async getAccessToken() {
    const now = Date.now();
    if (this.accessToken && now < this.tokenExpireTime) {
      return this.accessToken;
    }

    const response = await axios.get(`${WECHAT_API_BASE}/cgi-bin/token`, {
      params: {
        grant_type: 'client_credential',
        appid: this.appId,
        secret: this.appSecret
      }
    });

    if (response.data.access_token) {
      this.accessToken = response.data.access_token;
      this.tokenExpireTime = now + (response.data.expires_in - 300) * 1000;
      return this.accessToken;
    }
    throw new Error(`获取 access_token 失败：${response.data.errmsg}`);
  }
}

// 获取所有草稿列表
async function getAllDrafts(tokenManager) {
  const accessToken = await tokenManager.getAccessToken();
  const allDrafts = [];
  let offset = 0;
  const count = 20;

  while (true) {
    const response = await axios.post(
      `${WECHAT_API_BASE}/cgi-bin/draft/batchget?access_token=${accessToken}`,
      {
        offset,
        count,
        no_content: 1
      }
    );

    if (response.data.errcode) {
      throw new Error(`获取草稿列表失败：${response.data.errmsg}`);
    }

    const { item = [], total_count } = response.data;
    allDrafts.push(...item);

    if (allDrafts.length >= total_count) {
      break;
    }

    offset += count;

    // 如果获取到空列表但总数还未达到，可能是 API 限制，退出循环
    if (item.length === 0) {
      break;
    }
  }

  return allDrafts;
}

// 删除单个草稿
async function deleteSingleDraft(mediaId, tokenManager) {
  const accessToken = await tokenManager.getAccessToken();

  const response = await axios.post(
    `${WECHAT_API_BASE}/cgi-bin/draft/delete?access_token=${accessToken}`,
    {
      media_id: mediaId
    }
  );

  if (response.data.errcode && response.data.errcode !== 0) {
    throw new Error(response.data.errmsg);
  }

  return true;
}

// 主函数
async function deleteAllDrafts(confirm = false) {
  const config = loadConfig();
  const tokenManager = new AccessTokenManager(config.appId, config.appSecret);

  console.log('正在获取草稿列表...');

  // 获取所有草稿
  const drafts = await getAllDrafts(tokenManager);
  const total = drafts.length;

  if (total === 0) {
    return {
      success: true,
      message: '草稿箱为空，无需删除',
      total: 0,
      deleted: 0,
      failed: 0,
      errors: []
    };
  }

  console.log(`发现 ${total} 篇草稿`);

  if (!confirm) {
    return {
      success: false,
      message: `需要确认：请设置 confirm=true 以确认删除所有 ${total} 篇草稿`,
      total,
      deleted: 0,
      failed: 0,
      errors: []
    };
  }

  console.log('⚠️  开始删除所有草稿...');

  let deleted = 0;
  let failed = 0;
  const errors = [];

  for (let i = 0; i < drafts.length; i++) {
    const draft = drafts[i];
    const newsItem = draft.content?.news_item?.[0];
    const title = newsItem?.title || '无标题';

    try {
      await deleteSingleDraft(draft.media_id, tokenManager);
      deleted++;
      console.log(`✅ [${i + 1}/${total}] 已删除: ${title}`);
    } catch (error) {
      failed++;
      errors.push({ media_id: draft.media_id, title, error: error.message });
      console.error(`❌ [${i + 1}/${total}] 删除失败: ${title} - ${error.message}`);
    }

    // 添加延迟，避免请求过快
    if (i < drafts.length - 1) {
      await new Promise(resolve => setTimeout(resolve, 100));
    }
  }

  return {
    success: true,
    message: `成功删除 ${deleted} 篇草稿${failed > 0 ? `，${failed} 篇失败` : ''}`,
    total,
    deleted,
    failed,
    errors
  };
}

// CLI
if (require.main === module) {
  const args = process.argv.slice(2);
  const confirm = args[0] === 'true';

  if (!confirm) {
    // 先获取数量但不删除
    deleteAllDrafts(false)
      .then(result => {
        if (result.total === 0) {
          console.log('\n📭 草稿箱为空');
        } else {
          console.log(`\n⚠️  发现 ${result.total} 篇草稿`);
          console.log('🔒 需要确认才能删除');
          console.log('');
          console.log('如需删除，请运行:');
          console.log(`  node delete-all-drafts.js true`);
        }
      })
      .catch(error => {
        console.error('\n❌ 失败:', error.message);
        process.exit(1);
      });
  } else {
    deleteAllDrafts(true)
      .then(result => {
        console.log('\n' + '='.repeat(40));
        console.log('✅', result.message);
        console.log(`📊 总计: ${result.total}, 成功: ${result.deleted}, 失败: ${result.failed}`);

        if (result.errors.length > 0) {
          console.log('\n❌ 失败的草稿:');
          result.errors.forEach(err => {
            console.log(`  - ${err.title}: ${err.error}`);
          });
        }
      })
      .catch(error => {
        console.error('\n❌ 失败:', error.message);
        process.exit(1);
      });
  }
}

module.exports = { deleteAllDrafts };
