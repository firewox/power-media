#!/usr/bin/env node
/**
 * 获取微信公众号草稿箱文章列表
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

// 格式化时间戳
function formatTime(timestamp) {
  const date = new Date(timestamp * 1000);
  return date.toLocaleString('zh-CN');
}

// 主函数
async function getDraftList(offset = 0, count = 20) {
  // 限制 count 最大值
  if (count > 20) count = 20;

  const config = loadConfig();
  const tokenManager = new AccessTokenManager(config.appId, config.appSecret);

  console.log(`正在获取草稿列表 (offset: ${offset}, count: ${count})...`);

  const accessToken = await tokenManager.getAccessToken();

  const response = await axios.post(
    `${WECHAT_API_BASE}/cgi-bin/draft/batchget?access_token=${accessToken}`,
    {
      offset,
      count,
      no_content: 1  // 不返回内容，只返回基本信息
    }
  );

  if (response.data.errcode) {
    throw new Error(`获取草稿列表失败：${response.data.errmsg} (错误码: ${response.data.errcode})`);
  }

  const { total_count, item_count, item: items = [] } = response.data;

  // 格式化输出
  const formattedItems = items.map(draft => {
    const newsItem = draft.content?.news_item?.[0];
    return {
      media_id: draft.media_id,
      title: newsItem?.title || '无标题',
      author: newsItem?.author || '',
      digest: newsItem?.digest || '',
      create_time: draft.content?.create_time,
      update_time: draft.content?.update_time,
      create_time_formatted: formatTime(draft.content?.create_time),
      update_time_formatted: formatTime(draft.content?.update_time)
    };
  });

  return {
    success: true,
    total_count,
    item_count,
    items: formattedItems
  };
}

// CLI
if (require.main === module) {
  const args = process.argv.slice(2);
  const offset = parseInt(args[0]) || 0;
  const count = parseInt(args[1]) || 20;

  getDraftList(offset, count)
    .then(result => {
      console.log('\n✅ 获取成功');
      console.log(`📊 草稿总数: ${result.total_count}`);
      console.log(`📄 本次返回: ${result.item_count} 篇\n`);

      if (result.items.length > 0) {
        console.log('草稿列表:');
        console.log('-'.repeat(80));
        result.items.forEach((item, index) => {
          console.log(`${index + 1}. ${item.title}`);
          console.log(`   Media ID: ${item.media_id}`);
          if (item.author) console.log(`   作者: ${item.author}`);
          if (item.digest) console.log(`   摘要: ${item.digest.substring(0, 50)}${item.digest.length > 50 ? '...' : ''}`);
          console.log(`   更新时间: ${item.update_time_formatted}`);
          console.log('');
        });
      } else {
        console.log('暂无草稿');
      }
    })
    .catch(error => {
      console.error('\n❌ 失败:', error.message);
      process.exit(1);
    });
}

module.exports = { getDraftList };
