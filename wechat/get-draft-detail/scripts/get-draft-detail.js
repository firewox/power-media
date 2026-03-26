#!/usr/bin/env node
/**
 * 获取微信公众号草稿箱文章详情
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
  if (!timestamp) return '';
  const date = new Date(timestamp * 1000);
  return date.toLocaleString('zh-CN');
}

// 主函数
async function getDraftDetail(mediaId) {
  if (!mediaId) {
    throw new Error('mediaId 是必填参数');
  }

  const config = loadConfig();
  const tokenManager = new AccessTokenManager(config.appId, config.appSecret);

  console.log(`正在获取草稿详情: ${mediaId}...`);

  const accessToken = await tokenManager.getAccessToken();

  const response = await axios.post(
    `${WECHAT_API_BASE}/cgi-bin/draft/get?access_token=${accessToken}`,
    {
      media_id: mediaId
    }
  );

  if (response.data.errcode) {
    throw new Error(`获取草稿详情失败：${response.data.errmsg} (错误码: ${response.data.errcode})`);
  }

  const newsItem = response.data.news_item?.[0];
  if (!newsItem) {
    throw new Error('草稿内容为空或不存在');
  }

  return {
    success: true,
    media_id: mediaId,
    title: newsItem.title || '',
    author: newsItem.author || '',
    digest: newsItem.digest || '',
    content: newsItem.content || '',
    thumb_media_id: newsItem.thumb_media_id || '',
    show_cover_pic: newsItem.show_cover_pic || 0,
    url: newsItem.url || '',
    content_source_url: newsItem.content_source_url || '',
    need_open_comment: newsItem.need_open_comment || 0,
    only_fans_can_comment: newsItem.only_fans_can_comment || 0,
    create_time: response.data.create_time,
    update_time: response.data.update_time,
    create_time_formatted: formatTime(response.data.create_time),
    update_time_formatted: formatTime(response.data.update_time)
  };
}

// CLI
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.length < 1) {
    console.log('Usage: node get-draft-detail.js <mediaId>');
    console.log('');
    console.log('Example:');
    console.log('  node get-draft-detail.js xxxxxxxxxx');
    process.exit(1);
  }

  const [mediaId] = args;

  getDraftDetail(mediaId)
    .then(result => {
      console.log('\n✅ 获取成功\n');
      console.log('📄 草稿信息:');
      console.log('-'.repeat(80));
      console.log(`标题: ${result.title}`);
      console.log(`作者: ${result.author || '无'}`);
      console.log(`Media ID: ${result.media_id}`);
      if (result.digest) {
        console.log(`摘要: ${result.digest}`);
      }
      console.log(`创建时间: ${result.create_time_formatted}`);
      console.log(`更新时间: ${result.update_time_formatted}`);
      if (result.content_source_url) {
        console.log(`原文链接: ${result.content_source_url}`);
      }
      if (result.url) {
        console.log(`预览链接: ${result.url}`);
      }
      console.log(`评论: ${result.need_open_comment ? '开启' : '关闭'}`);
      console.log(`粉丝才可评论: ${result.only_fans_can_comment ? '是' : '否'}`);
      console.log('');
      console.log('内容预览:');
      console.log('-'.repeat(80));
      // 显示内容的前 500 个字符
      const contentPreview = result.content.replace(/<[^>]*>/g, '').substring(0, 500);
      console.log(contentPreview + (contentPreview.length >= 500 ? '...' : ''));
    })
    .catch(error => {
      console.error('\n❌ 失败:', error.message);
      process.exit(1);
    });
}

module.exports = { getDraftDetail };
