#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const axios = require('axios');
const {
  AccessTokenManager,
  createStageError,
  exitWithError,
  hasJsonFlag,
  loadConfig,
  printResult,
  resolveImageSource
} = require('../../lib/wechat-common');

function extractMarkdownImages(mdContent) {
  return [...mdContent.matchAll(/!\[([^\]]*)\]\(([^)]+)\)/g)].map(match => ({
    alt: match[1],
    src: match[2]
  }));
}

async function validateMarkdown(filePath) {
  const resolvedPath = path.isAbsolute(filePath) ? filePath : path.resolve(process.cwd(), filePath);
  if (!fs.existsSync(resolvedPath)) {
    throw createStageError('validate-file', `Markdown 文件不存在: ${resolvedPath}`, { resolvedPath });
  }

  const config = loadConfig();
  const tokenManager = new AccessTokenManager(axios, config.appId, config.appSecret);
  const content = fs.readFileSync(resolvedPath, 'utf-8');
  const images = extractMarkdownImages(content);

  const imageResults = images.map(image => {
    const isRemote = /^https?:\/\//i.test(image.src);
    const resolved = isRemote ? image.src : resolveImageSource(image.src, path.dirname(resolvedPath));
    return {
      src: image.src,
      resolved,
      exists: isRemote || fs.existsSync(resolved),
      type: isRemote ? 'remote' : 'local'
    };
  });

  const missingImages = imageResults.filter(item => !item.exists);
  if (missingImages.length > 0) {
    throw createStageError('validate-images', 'Markdown 中存在不可读取的本地图片', {
      missingImages
    });
  }

  await tokenManager.getAccessToken();

  return {
    success: true,
    stage: 'validate-markdown',
    message: 'Markdown 发布预检通过',
    file_path: resolvedPath,
    image_count: imageResults.length,
    images: imageResults,
    config_source: config.source
  };
}

if (require.main === module) {
  const args = process.argv.slice(2);
  const asJson = hasJsonFlag(args);
  const filePath = args.find(arg => !arg.startsWith('--'));

  if (!filePath) {
    exitWithError(createStageError('validate-args', '用法: node validate-markdown.js <filePath> [--json]'), asJson);
  }

  validateMarkdown(filePath)
    .then(result => printResult(result, asJson))
    .catch(error => exitWithError(error, asJson));
}

module.exports = { validateMarkdown };
