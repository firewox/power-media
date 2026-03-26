#!/usr/bin/env node
/**
 * 删除微信公众号草稿箱文章
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

// 主函数
async function deleteDraft(mediaId) {
  if (!mediaId) {
    throw new Error('mediaId 是必填参数');
  }

  const config = loadConfig();
  const tokenManager = new AccessTokenManager(config.appId, config.appSecret);

  console.log(`正在删除草稿: ${mediaId}...`);

  const accessToken = await tokenManager.getAccessToken();

  const response = await axios.post(
    `${WECHAT_API_BASE}/cgi-bin/draft/delete?access_token=${accessToken}`,
    {
      media_id: mediaId
    }
  );

  if (response.data.errcode && response.data.errcode !== 0) {
    throw new Error(`删除草稿失败：${response.data.errmsg} (错误码: ${response.data.errcode})`);
  }

  return {
    success: true,
    message: '草稿删除成功',
    media_id: mediaId
  };
}

// CLI
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.length < 1) {
    console.log('Usage: node delete-draft.js <mediaId>');
    console.log('');
    console.log('Example:');
    console.log('  node delete-draft.js xxxxxxxxxx');
    process.exit(1);
  }

  const [mediaId] = args;

  deleteDraft(mediaId)
    .then(result => {
      console.log('\n✅', result.message);
      console.log('🗑️  Media ID:', result.media_id);
    })
    .catch(error => {
      console.error('\n❌ 失败:', error.message);
      process.exit(1);
    });
}

module.exports = { deleteDraft };
