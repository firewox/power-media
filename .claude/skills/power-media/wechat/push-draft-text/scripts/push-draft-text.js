#!/usr/bin/env node
/**
 * 推送文本/Markdown 内容到微信公众号草稿箱
 */
const axios = require('axios');
const FormData = require('form-data');
const marked = require('marked');
const hljs = require('highlight.js');
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

const DEFAULT_P_STYLE = 'color:#333333;font-size:16px;line-height:1.75;';

async function uploadRemoteImage(imageUrl, tokenManager) {
  const accessToken = await tokenManager.getAccessToken();
  const image = await readImageSource(require('fs'), axios, imageUrl, process.cwd());
  const formData = new FormData();
  formData.append('media', image.data, { filename: image.filename, contentType: image.contentType });

  let response;
  try {
    response = await axios.post(
      `${WECHAT_API_BASE}/cgi-bin/material/add_material?access_token=${accessToken}&type=image`,
      formData,
      { headers: formData.getHeaders(), timeout: 30000 }
    );
  } catch (error) {
    throw wrapError('upload-image', `上传图片失败: ${imageUrl}`, error, { imageUrl });
  }

  if (response.data && response.data.media_id) {
    return response.data;
  }

  throw createStageError('upload-image', `上传图片失败: ${imageUrl}`, {
    errcode: response.data?.errcode,
    rawError: response.data?.errmsg,
    responseBody: response.data
  });
}

async function uploadGeneratedCover(tokenManager) {
  const accessToken = await tokenManager.getAccessToken();
  const coverBuffer = await sharp(Buffer.from(`
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
  `)).png().toBuffer();

  const formData = new FormData();
  formData.append('media', coverBuffer, { filename: 'cover.png', contentType: 'image/png' });

  let response;
  try {
    response = await axios.post(
      `${WECHAT_API_BASE}/cgi-bin/material/add_material?access_token=${accessToken}&type=image`,
      formData,
      { headers: formData.getHeaders(), timeout: 30000 }
    );
  } catch (error) {
    throw wrapError('upload-cover', '上传封面图请求失败', error);
  }

  if (response.data && response.data.media_id) {
    return response.data.media_id;
  }

  throw createStageError('upload-cover', '上传封面图失败', {
    errcode: response.data?.errcode,
    rawError: response.data?.errmsg,
    responseBody: response.data
  });
}

function generateDigest(content, maxLength = 120) {
  const text = content.replace(/[#*\[\]()\-`]/g, '').replace(/\s+/g, ' ').trim();
  return text.length <= maxLength ? text : `${text.substring(0, maxLength)}...`;
}

async function processContent(content, isMarkdown, tokenManager) {
  let processedContent = content;
  let imageCount = 0;
  const warnings = [];

  if (isMarkdown) {
    const matches = [...content.matchAll(/!\[([^\]]*)\]\(([^)]+)\)/g)];
    for (const match of matches) {
      const [fullMatch, alt, imageUrl] = match;
      if (!/^https?:\/\//i.test(imageUrl)) {
        warnings.push({ image: imageUrl, message: '文本模式仅自动上传网络图片，已保留原始路径' });
        continue;
      }
      try {
        const result = await uploadRemoteImage(imageUrl, tokenManager);
        processedContent = processedContent.replace(fullMatch, `![${alt}](${result.url || imageUrl})`);
        imageCount += 1;
      } catch (error) {
        warnings.push({ image: imageUrl, message: error.message });
      }
    }

    processedContent = processedContent.replace(/```(\w*)\n([\s\S]*?)```/g, (m, lang, code) => {
      const highlighted = lang && lang !== 'text'
        ? hljs.highlight(code, { language: lang }).value
        : hljs.highlightAuto(code).value;
      return `<pre style="background:#f5f5f5;padding:12px;border-radius:6px;overflow:auto;"><code>${highlighted}</code></pre>`;
    });

    let html = marked.parse(processedContent, { breaks: true, gfm: true });
    html = html.replace(/<p([^>]*)>/gi, `<p style="${DEFAULT_P_STYLE}"$1>`);
    return { html, imageCount, warnings };
  }

  return {
    html: `<p style="${DEFAULT_P_STYLE}">${content.replace(/\n/g, '<br>')}</p>`,
    imageCount,
    warnings
  };
}

async function pushDraftText({ content, title, digest, sourceUrl, isMarkdown = true }) {
  if (!content || !title) {
    throw createStageError('validate-args', 'content 和 title 是必填参数');
  }

  const config = loadConfig();
  const tokenManager = new AccessTokenManager(axios, config.appId, config.appSecret);
  const processed = await processContent(content, isMarkdown, tokenManager);
  const thumbMediaId = await uploadGeneratedCover(tokenManager);
  const accessToken = await tokenManager.getAccessToken();

  let response;
  try {
    response = await axios.post(
      `${WECHAT_API_BASE}/cgi-bin/draft/add?access_token=${accessToken}`,
      {
        articles: [{
          title,
          author: config.defaultAuthor,
          digest: digest || generateDigest(content),
          content: processed.html,
          thumb_media_id: thumbMediaId,
          need_open_comment: config.needOpenComment ? 1 : 0,
          only_fans_can_comment: config.onlyFansCanComment ? 1 : 0,
          source_url: sourceUrl || ''
        }]
      },
      { timeout: 30000 }
    );
  } catch (error) {
    throw wrapError('create-draft', '创建草稿请求失败', error);
  }

  if (!response.data?.media_id) {
    throw createStageError('create-draft', '创建草稿失败', {
      errcode: response.data?.errcode,
      rawError: response.data?.errmsg,
      responseBody: response.data
    });
  }

  return {
    success: true,
    stage: 'create-draft',
    message: '文章成功添加到草稿箱',
    media_id: response.data.media_id,
    image_count: processed.imageCount,
    warnings: processed.warnings
  };
}

if (require.main === module) {
  const args = process.argv.slice(2);
  const asJson = hasJsonFlag(args);
  const filtered = args.filter(arg => arg !== '--json');

  if (filtered.length < 2) {
    exitWithError(createStageError('validate-args', '用法: node push-draft-text.js <content> <title> [digest] [sourceUrl] [isMarkdown] [--json]'), asJson);
  }

  const [content, title, digest, sourceUrl, isMarkdownStr] = filtered;
  const isMarkdown = isMarkdownStr !== 'false';

  pushDraftText({ content, title, digest, sourceUrl, isMarkdown })
    .then(result => {
      if (asJson) {
        printResult(result, true);
        return;
      }
      console.log('\n✅', result.message);
      console.log(`📝 Media ID: ${result.media_id}`);
      if (result.image_count > 0) {
        console.log(`🖼️ 已处理图片: ${result.image_count} 张`);
      }
      if (result.warnings.length > 0) {
        result.warnings.forEach(item => console.log(`⚠️ ${item.image}: ${item.message}`));
      }
    })
    .catch(error => exitWithError(error, asJson));
}

module.exports = { pushDraftText };
