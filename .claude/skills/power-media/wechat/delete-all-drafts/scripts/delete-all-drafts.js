#!/usr/bin/env node
/**
 * 批量删除微信公众号草稿箱所有文章
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

async function getAllDrafts(tokenManager) {
  const accessToken = await tokenManager.getAccessToken();
  const drafts = [];
  let offset = 0;
  while (true) {
    let response;
    try {
      response = await axios.post(
        `${WECHAT_API_BASE}/cgi-bin/draft/batchget?access_token=${accessToken}`,
        { offset, count: 20, no_content: 1 },
        { timeout: 30000 }
      );
    } catch (error) {
      throw wrapError('delete-all-drafts:list', '获取草稿列表请求失败', error);
    }

    if (response.data.errcode) {
      throw createStageError('delete-all-drafts:list', '获取草稿列表失败', {
        errcode: response.data.errcode,
        rawError: response.data.errmsg,
        responseBody: response.data
      });
    }

    drafts.push(...(response.data.item || []));
    if (drafts.length >= (response.data.total_count || 0) || (response.data.item || []).length === 0) {
      return drafts;
    }
    offset += 20;
  }
}

async function deleteSingleDraft(mediaId, tokenManager) {
  const accessToken = await tokenManager.getAccessToken();
  try {
    const response = await axios.post(
      `${WECHAT_API_BASE}/cgi-bin/draft/delete?access_token=${accessToken}`,
      { media_id: mediaId },
      { timeout: 30000 }
    );
    if (response.data.errcode && response.data.errcode !== 0) {
      throw createStageError('delete-all-drafts:item', '删除草稿失败', {
        errcode: response.data.errcode,
        rawError: response.data.errmsg,
        responseBody: response.data,
        mediaId
      });
    }
  } catch (error) {
    if (error.stage) {
      throw error;
    }
    throw wrapError('delete-all-drafts:item', '删除草稿请求失败', error, { mediaId });
  }
}

async function deleteAllDrafts(confirm = false) {
  const config = loadConfig();
  const tokenManager = new AccessTokenManager(axios, config.appId, config.appSecret);
  const drafts = await getAllDrafts(tokenManager);

  if (!confirm) {
    return {
      success: false,
      stage: 'delete-all-drafts:confirm',
      message: `需要确认：请设置 confirm=true 以确认删除所有 ${drafts.length} 篇草稿`,
      total: drafts.length,
      deleted: 0,
      failed: 0,
      errors: []
    };
  }

  let deleted = 0;
  let failed = 0;
  const errors = [];

  for (const draft of drafts) {
    try {
      await deleteSingleDraft(draft.media_id, tokenManager);
      deleted += 1;
    } catch (error) {
      failed += 1;
      errors.push({
        media_id: draft.media_id,
        title: draft.content?.news_item?.[0]?.title || '无标题',
        message: error.message
      });
    }
  }

  return {
    success: true,
    stage: 'delete-all-drafts',
    message: `成功删除 ${deleted} 篇草稿${failed > 0 ? `，${failed} 篇失败` : ''}`,
    total: drafts.length,
    deleted,
    failed,
    errors
  };
}

if (require.main === module) {
  const args = process.argv.slice(2);
  const asJson = hasJsonFlag(args);
  const confirm = args.includes('true');

  deleteAllDrafts(confirm)
    .then(result => {
      if (asJson) {
        printResult(result, true);
        return;
      }
      if (!confirm) {
        console.log(result.message);
        return;
      }
      console.log('\n✅', result.message);
      console.log(`📊 总计: ${result.total}, 成功: ${result.deleted}, 失败: ${result.failed}`);
    })
    .catch(error => exitWithError(error, asJson));
}

module.exports = { deleteAllDrafts };
