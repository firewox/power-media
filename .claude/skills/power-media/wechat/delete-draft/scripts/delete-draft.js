#!/usr/bin/env node
/**
 * 删除微信公众号草稿箱文章
 */
const axios = require('axios');
const {
  AccessTokenManager,
  WECHAT_API_BASE,
  createStageError,
  exitWithError,
  hasJsonFlag,
  loadConfig,
  printResult,
  wrapError
} = require('../../lib/wechat-common');

async function deleteDraft(mediaId) {
  if (!mediaId) {
    throw createStageError('validate-args', 'mediaId 是必填参数');
  }

  const config = loadConfig();
  const tokenManager = new AccessTokenManager(axios, config.appId, config.appSecret);
  const accessToken = await tokenManager.getAccessToken();

  let response;
  try {
    response = await axios.post(
      `${WECHAT_API_BASE}/cgi-bin/draft/delete?access_token=${accessToken}`,
      { media_id: mediaId },
      { timeout: 30000 }
    );
  } catch (error) {
    throw wrapError('delete-draft', '删除草稿请求失败', error, { mediaId });
  }

  if (response.data.errcode && response.data.errcode !== 0) {
    throw createStageError('delete-draft', '删除草稿失败', {
      errcode: response.data.errcode,
      rawError: response.data.errmsg,
      responseBody: response.data,
      mediaId
    });
  }

  return {
    success: true,
    stage: 'delete-draft',
    message: '草稿删除成功',
    media_id: mediaId
  };
}

if (require.main === module) {
  const args = process.argv.slice(2);
  const asJson = hasJsonFlag(args);
  const mediaId = args.find(arg => !arg.startsWith('--'));
  if (!mediaId) {
    exitWithError(createStageError('validate-args', '用法: node delete-draft.js <mediaId> [--json]'), asJson);
  }

  deleteDraft(mediaId)
    .then(result => {
      if (asJson) {
        printResult(result, true);
        return;
      }
      console.log('\n✅', result.message);
      console.log('🗑️ Media ID:', result.media_id);
    })
    .catch(error => exitWithError(error, asJson));
}

module.exports = { deleteDraft };
