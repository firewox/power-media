#!/usr/bin/env node
/**
 * 上传图片到微信公众号素材库
 */
const fs = require('fs');
const axios = require('axios');
const FormData = require('form-data');
const {
  AccessTokenManager,
  WECHAT_API_BASE,
  createStageError,
  exitWithError,
  hasJsonFlag,
  loadConfig,
  printResult,
  readImageSource,
  wrapError
} = require('../../lib/wechat-common');

async function uploadImage(imageSource, isTemporary = false) {
  if (!imageSource) {
    throw createStageError('validate-args', 'imageSource 是必填参数');
  }

  const config = loadConfig();
  const tokenManager = new AccessTokenManager(axios, config.appId, config.appSecret);
  const accessToken = await tokenManager.getAccessToken();
  const image = await readImageSource(fs, axios, imageSource, process.cwd());

  if (image.data.length > 2 * 1024 * 1024) {
    throw createStageError('validate-image', '图片大小超过 2MB 限制', {
      imageSource,
      size: image.data.length
    });
  }

  const form = new FormData();
  form.append('media', image.data, {
    filename: image.filename,
    contentType: image.contentType
  });

  const endpoint = isTemporary
    ? `/cgi-bin/media/upload?access_token=${accessToken}&type=image`
    : `/cgi-bin/material/add_material?access_token=${accessToken}&type=image`;

  let response;
  try {
    response = await axios.post(`${WECHAT_API_BASE}${endpoint}`, form, {
      headers: form.getHeaders(),
      timeout: 60000
    });
  } catch (error) {
    throw wrapError('upload-image', '上传图片请求失败', error, { imageSource });
  }

  if (response.data.errcode) {
    throw createStageError('upload-image', '上传图片失败', {
      errcode: response.data.errcode,
      rawError: response.data.errmsg,
      responseBody: response.data,
      imageSource
    });
  }

  return {
    success: true,
    stage: 'upload-image',
    message: '图片上传成功',
    media_id: response.data.media_id,
    url: response.data.url || '',
    type: isTemporary ? 'temporary' : 'permanent',
    source: image.resolvedPath || imageSource
  };
}

if (require.main === module) {
  const args = process.argv.slice(2);
  const asJson = hasJsonFlag(args);
  const filtered = args.filter(arg => arg !== '--json');
  const imageSource = filtered.find(arg => !arg.startsWith('--'));
  const isTemporary = filtered.includes('--temporary');

  if (!imageSource) {
    exitWithError(createStageError('validate-args', '用法: node upload-image.js <图片URL或路径> [--temporary] [--json]'), asJson);
  }

  uploadImage(imageSource, isTemporary)
    .then(result => {
      if (asJson) {
        printResult(result, true);
        return;
      }
      console.log('\n✅', result.message);
      console.log(`Media ID: ${result.media_id}`);
      if (result.url) {
        console.log(`URL: ${result.url}`);
      }
    })
    .catch(error => exitWithError(error, asJson));
}

module.exports = { uploadImage };
