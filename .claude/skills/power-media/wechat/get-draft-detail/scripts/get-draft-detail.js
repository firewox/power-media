#!/usr/bin/env node
/**
 * 获取微信公众号草稿箱文章详情
 */
const axios = require('axios');
const {
  AccessTokenManager,
  WECHAT_API_BASE,
  createStageError,
  exitWithError,
  formatTime,
  hasJsonFlag,
  loadConfig,
  printResult,
  wrapError
} = require('../../lib/wechat-common');

async function getDraftDetail(mediaId) {
  if (!mediaId) {
    throw createStageError('validate-args', 'mediaId 是必填参数');
  }

  const config = loadConfig();
  const tokenManager = new AccessTokenManager(axios, config.appId, config.appSecret);
  const accessToken = await tokenManager.getAccessToken();

  let response;
  try {
    response = await axios.post(
      `${WECHAT_API_BASE}/cgi-bin/draft/get?access_token=${accessToken}`,
      { media_id: mediaId },
      { timeout: 30000 }
    );
  } catch (error) {
    throw wrapError('get-draft-detail', '获取草稿详情请求失败', error, { mediaId });
  }

  if (response.data.errcode) {
    throw createStageError('get-draft-detail', '获取草稿详情失败', {
      errcode: response.data.errcode,
      rawError: response.data.errmsg,
      responseBody: response.data,
      mediaId
    });
  }

  const newsItem = response.data.news_item?.[0];
  if (!newsItem) {
    throw createStageError('get-draft-detail', '草稿内容为空或不存在', { mediaId });
  }

  return {
    success: true,
    stage: 'get-draft-detail',
    message: '获取草稿详情成功',
    media_id: mediaId,
    title: newsItem.title || '',
    author: newsItem.author || '',
    digest: newsItem.digest || '',
    content: newsItem.content || '',
    thumb_media_id: newsItem.thumb_media_id || '',
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

if (require.main === module) {
  const args = process.argv.slice(2);
  const asJson = hasJsonFlag(args);
  const mediaId = args.find(arg => !arg.startsWith('--'));

  if (!mediaId) {
    exitWithError(createStageError('validate-args', '用法: node get-draft-detail.js <mediaId> [--json]'), asJson);
  }

  getDraftDetail(mediaId)
    .then(result => {
      if (asJson) {
        printResult(result, true);
        return;
      }
      console.log('\n✅', result.message);
      console.log(`标题: ${result.title}`);
      console.log(`Media ID: ${result.media_id}`);
      console.log(`更新时间: ${result.update_time_formatted}`);
    })
    .catch(error => exitWithError(error, asJson));
}

module.exports = { getDraftDetail };
