#!/usr/bin/env node
/**
 * 从 Markdown 文件推送文章到微信公众号草稿箱
 */
const fs = require('fs');
const path = require('path');
const axios = require('axios');
const FormData = require('form-data');
const sharp = require('sharp');
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
const { validateMarkdown } = require('../../validate-markdown/scripts/validate-markdown');
const { convert: md2wechatConvert } = require('../../markdown-to-wechat-html/scripts/md2wechat');

async function uploadImageSource(imageSource, tokenManager, baseDir) {
  const accessToken = await tokenManager.getAccessToken();
  const image = await readImageSource(fs, axios, imageSource, baseDir);

  const formData = new FormData();
  formData.append('media', image.data, { filename: image.filename, contentType: image.contentType });
  formData.append('type', 'image');

  let response;
  try {
    response = await axios.post(
      `${WECHAT_API_BASE}/cgi-bin/material/add_material?access_token=${accessToken}&type=image`,
      formData,
      { headers: formData.getHeaders(), timeout: 30000 }
    );
  } catch (error) {
    throw wrapError('upload-image', `上传图片失败: ${imageSource}`, error, {
      imageSource,
      resolvedPath: image.resolvedPath
    });
  }

  if (response.data && response.data.media_id) {
    return {
      media_id: response.data.media_id,
      url: response.data.url || '',
      resolvedPath: image.resolvedPath
    };
  }

  throw createStageError('upload-image', `上传图片失败: ${imageSource}`, {
    imageSource,
    errcode: response.data?.errcode,
    rawError: response.data?.errmsg,
    responseBody: response.data
  });
}

async function markdownToHtml(mdContent, markdownFilePath, tokenManager) {
  let processedContent = mdContent;
  const warnings = [];
  let imageCount = 0;
  let firstImageMediaId = null;

  const imageRegex = /!\[([^\]]*)\]\(([^)]+)\)/g;
  const matches = [...mdContent.matchAll(imageRegex)];

  for (const match of matches) {
    const [fullMatch, alt, imageUrl] = match;
    try {
      const result = await uploadImageSource(imageUrl, tokenManager, path.dirname(markdownFilePath));
      imageCount += 1;
      if (!firstImageMediaId) {
        firstImageMediaId = result.media_id;
      }
      processedContent = processedContent.replace(fullMatch, `![${alt}](${result.url})`);
    } catch (error) {
      warnings.push({
        stage: error.stage || 'upload-image',
        image: imageUrl,
        message: error.message
      });
    }
  }

  const html = md2wechatConvert(processedContent);

  return { html, imageCount, firstImageMediaId, warnings };
}

async function generateDefaultCoverImage() {
  const svgBuffer = Buffer.from(`
    <svg width="900" height="500" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
        </linearGradient>
      </defs>
      <rect width="900" height="500" fill="url(#grad)"/>
      <text x="50%" y="50%" font-family="Arial" font-size="120" font-weight="bold"
            fill="white" text-anchor="middle" dominant-baseline="central">文章</text>
    </svg>
  `);

  return sharp(svgBuffer).png().toBuffer();
}

async function getCoverImage(firstImageMediaId, tokenManager, markdownFilePath) {
  if (firstImageMediaId) {
    return firstImageMediaId;
  }

  const coverCandidates = [
    path.resolve(path.dirname(markdownFilePath), 'thumbnail.png'),
    path.resolve(path.dirname(markdownFilePath), 'thumbnail.jpg'),
    path.resolve(path.dirname(markdownFilePath), 'default-cover.png')
  ];

  for (const candidate of coverCandidates) {
    if (!fs.existsSync(candidate)) {
      continue;
    }
    const result = await uploadImageSource(candidate, tokenManager, path.dirname(markdownFilePath));
    return result.media_id;
  }

  const tempPath = path.resolve(path.dirname(markdownFilePath), '.temp-wechat-cover.png');
  fs.writeFileSync(tempPath, await generateDefaultCoverImage());
  try {
    const result = await uploadImageSource(tempPath, tokenManager, path.dirname(markdownFilePath));
    return result.media_id;
  } finally {
    if (fs.existsSync(tempPath)) {
      fs.unlinkSync(tempPath);
    }
  }
}

async function createDraftArticle(payload, tokenManager) {
  const accessToken = await tokenManager.getAccessToken();
  let response;
  try {
    response = await axios.post(
      `${WECHAT_API_BASE}/cgi-bin/draft/add?access_token=${accessToken}`,
      payload,
      { timeout: 30000 }
    );
  } catch (error) {
    throw wrapError('create-draft', '创建草稿请求失败', error);
  }

  if (response.data && response.data.media_id) {
    return response.data.media_id;
  }

  throw createStageError('create-draft', '创建草稿失败', {
    errcode: response.data?.errcode,
    rawError: response.data?.errmsg,
    responseBody: response.data
  });
}

async function pushDraftFromFile(filePath, title, digest, sourceUrl) {
  if (!filePath || !title) {
    throw createStageError('validate-args', 'filePath 和 title 是必填参数');
  }

  await validateMarkdown(filePath);

  const config = loadConfig();
  const tokenManager = new AccessTokenManager(axios, config.appId, config.appSecret);
  const resolvedPath = path.isAbsolute(filePath) ? filePath : path.resolve(process.cwd(), filePath);
  const mdContent = fs.readFileSync(resolvedPath, 'utf-8');

  const { html, imageCount, firstImageMediaId, warnings } = await markdownToHtml(mdContent, resolvedPath, tokenManager);
  const thumbMediaId = await getCoverImage(firstImageMediaId, tokenManager, resolvedPath);

  const mediaId = await createDraftArticle({
    articles: [{
      title,
      author: config.defaultAuthor,
      digest: digest || '',
      content: html,
      thumb_media_id: thumbMediaId,
      need_open_comment: config.needOpenComment ? 1 : 0,
      only_fans_can_comment: config.onlyFansCanComment ? 1 : 0,
      source_url: sourceUrl || ''
    }]
  }, tokenManager);

  return {
    success: true,
    stage: 'create-draft',
    message: '文章成功添加到草稿箱',
    media_id: mediaId,
    file_path: resolvedPath,
    image_count: imageCount,
    warnings,
    first_image_media_id: firstImageMediaId || null
  };
}

if (require.main === module) {
  const args = process.argv.slice(2);
  const asJson = hasJsonFlag(args);
  const filteredArgs = args.filter(arg => arg !== '--json');

  if (filteredArgs.length < 2) {
    exitWithError(createStageError('validate-args', '用法: node push-draft-file.js <filePath> <title> [digest] [sourceUrl] [--json]'), asJson);
  }

  const [filePath, title, digest, sourceUrl] = filteredArgs;

  pushDraftFromFile(filePath, title, digest, sourceUrl)
    .then(result => {
      if (asJson) {
        printResult(result, true);
        return;
      }
      console.log('\n✅', result.message);
      console.log('📝 Media ID:', result.media_id);
      console.log('🖼️ 已处理图片:', result.image_count, '张');
      if (result.first_image_media_id) {
        console.log('📸 首图 Media ID:', result.first_image_media_id);
      }
      if (result.warnings.length > 0) {
        console.log('⚠️ 警告:');
        result.warnings.forEach(item => console.log(`  - ${item.image}: ${item.message}`));
      }
    })
    .catch(error => exitWithError(error, asJson));
}

module.exports = { pushDraftFromFile };
