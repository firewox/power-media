#!/usr/bin/env node
/**
 * 获取微信公众号草稿箱文章列表
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

async function getDraftList(offset = 0, count = 20) {
  const safeCount = Math.min(Number(count) || 20, 20);
  const safeOffset = Number(offset) || 0;
  const config = loadConfig();
  const tokenManager = new AccessTokenManager(axios, config.appId, config.appSecret);
  const accessToken = await tokenManager.getAccessToken();

  let response;
  try {
    response = await axios.post(
      `${WECHAT_API_BASE}/cgi-bin/draft/batchget?access_token=${accessToken}`,
      { offset: safeOffset, count: safeCount, no_content: 1 },
      { timeout: 30000 }
    );
  } catch (error) {
    throw wrapError('get-draft-list', '获取草稿列表请求失败', error);
  }

  if (response.data.errcode) {
    throw createStageError('get-draft-list', '获取草稿列表失败', {
      errcode: response.data.errcode,
      rawError: response.data.errmsg,
      responseBody: response.data
    });
  }

  const items = (response.data.item || []).map(draft => {
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
    stage: 'get-draft-list',
    message: '获取草稿列表成功',
    total_count: response.data.total_count,
    item_count: response.data.item_count,
    items
  };
}

if (require.main === module) {
  const args = process.argv.slice(2);
  const asJson = hasJsonFlag(args);
  const filtered = args.filter(arg => arg !== '--json');
  const offset = filtered[0] || 0;
  const count = filtered[1] || 20;

  getDraftList(offset, count)
    .then(result => {
      if (asJson) {
        printResult(result, true);
        return;
      }
      console.log('\n✅', result.message);
      console.log(`📊 草稿总数: ${result.total_count}`);
      console.log(`📄 本次返回: ${result.item_count}`);
      result.items.forEach((item, index) => {
        console.log(`${index + 1}. ${item.title}`);
        console.log(`   Media ID: ${item.media_id}`);
        console.log(`   更新时间: ${item.update_time_formatted}`);
      });
    })
    .catch(error => exitWithError(error, asJson));
}

module.exports = { getDraftList };
