#!/usr/bin/env node
/**
 * 从 Markdown 文件推送文章到微信公众号草稿箱
 */

const fs = require('fs');
const path = require('path');

// 依赖检查
let axios, FormData, marked, sanitizeHtml, hljs, sharp;

try {
  axios = require('axios');
  FormData = require('form-data');
  marked = require('marked');
  sanitizeHtml = require('sanitize-html');
  hljs = require('highlight.js');
  sharp = require('sharp');
} catch (e) {
  console.error('缺少依赖包，请先安装：npm install axios form-data marked sanitize-html highlight.js sharp');
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

  return {
    appId,
    appSecret,
    defaultAuthor: process.env.WECHAT_DEFAULT_AUTHOR || '',
    needOpenComment: process.env.WECHAT_NEED_OPEN_COMMENT === 'true',
    onlyFansCanComment: process.env.WECHAT_ONLY_FANS_CAN_COMMENT === 'true'
  };
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

// 下载网络图片
async function downloadImage(imageUrl) {
  let retryCount = 0;
  const maxRetries = 3;

  while (retryCount < maxRetries) {
    try {
      const response = await axios.get(imageUrl, {
        responseType: 'arraybuffer',
        timeout: 30000,
        headers: {
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
      });

      return {
        data: Buffer.from(response.data),
        contentType: response.headers['content-type'] || 'image/jpeg',
        filename: path.basename(imageUrl) || 'image.jpg'
      };
    } catch (error) {
      retryCount++;
      if (retryCount === maxRetries) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
    }
  }
}

// 上传图片到微信
async function uploadImage(imageUrl, tokenManager) {
  const accessToken = await tokenManager.getAccessToken();

  let imageData, contentType, filename;

  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    const downloaded = await downloadImage(imageUrl);
    imageData = downloaded.data;
    contentType = downloaded.contentType;
    filename = downloaded.filename;
  } else {
    const fullPath = path.isAbsolute(imageUrl) ? imageUrl : path.resolve(process.cwd(), imageUrl);
    if (!fs.existsSync(fullPath)) {
      throw new Error(`图片文件不存在：${fullPath}`);
    }
    imageData = fs.readFileSync(fullPath);
    const ext = path.extname(fullPath).toLowerCase();
    contentType = ext === '.png' ? 'image/png' : ext === '.gif' ? 'image/gif' : 'image/jpeg';
    filename = path.basename(fullPath);
  }

  const formData = new FormData();
  formData.append('media', imageData, { filename, contentType });
  formData.append('type', 'image');

  const response = await axios.post(
    `${WECHAT_API_BASE}/cgi-bin/material/add_material?access_token=${accessToken}&type=image`,
    formData,
    { headers: formData.getHeaders(), timeout: 30000 }
  );

  if (response.data.media_id) {
    return {
      media_id: response.data.media_id,
      url: response.data.url || ''
    };
  }
  throw new Error(`上传图片失败：${response.data.errmsg}`);
}

// Markdown 转换样式
const DEFAULT_STYLES = {
  title: {
    font_size: '24px', color: '#DC143C', text_align: 'center',
    line_height: '1.2', letter_spacing: '1px', margin: '0.5em 0', font_weight: 'bold'
  },
  h2: {
    font_size: '22px', color: '#0000CD', line_height: '1.4',
    margin: '1.5em 0 0.8em 0', font_weight: 'bold',
    border_left: '4px solid #DC143C', padding_left: '12px'
  },
  h3: {
    font_size: '20px', color: '#0000CD', line_height: '1.5',
    margin: '2em 0 0.8em 0', font_weight: 'bold'
  },
  p: { color: '#333333', font_size: '16px', line_height: '1.75' },
  strong: { color: '#DC143C' },
  blockquote: {
    background: '#f5f5f5', border_left: '4px solid #DC143C',
    padding: '12px 16px', margin: '1em 0', color: '#666666'
  },
  code: { background: '#f5f5f5', padding: '2px 6px', border_radius: '4px' },
  pre: { background: '#f5f5f5', padding: '12px', border_radius: '6px', overflow: 'auto' },
  img: {
    max_width: '100%', border_radius: '8px',
    box_shadow: '0 4px 6px rgba(0,0,0,0.15)', display: 'block', margin: '1.5em auto'
  },
  table: { width: '100%', border_collapse: 'collapse', margin: '1em 0' },
  th: { background: '#f0f0f0', padding: '10px', text_align: 'center', border: '1px solid #dddddd', font_weight: 'bold' },
  td: { padding: '10px', border: '1px solid #dddddd', text_align: 'center' }
};

function buildStyleString(styles) {
  return Object.entries(styles).map(([k, v]) => `${k.replace(/_/g, '-')}:${v}`).join(';') + ';';
}

// Markdown 转 HTML
async function markdownToHtml(mdContent, markdownFilePath, tokenManager) {
  let processedContent = mdContent;
  let imageCount = 0;
  let firstImageMediaId = null;

  // 处理图片
  const imageRegex = /!\[([^\]]*)\]\(([^)]+)\)/g;
  const matches = [...mdContent.matchAll(imageRegex)];

  for (const match of matches) {
    const [fullMatch, alt, imageUrl] = match;
    let resolvedUrl = imageUrl;

    if (!imageUrl.startsWith('http') && markdownFilePath) {
      resolvedUrl = path.resolve(path.dirname(markdownFilePath), imageUrl);
    }

    try {
      const result = await uploadImage(resolvedUrl, tokenManager);
      imageCount++;
      if (!firstImageMediaId) firstImageMediaId = result.media_id;
      processedContent = processedContent.replace(fullMatch, `![${alt}](${result.url})`);
    } catch (e) {
      console.error(`图片上传失败：${imageUrl}`, e.message);
    }
  }

  // 代码高亮
  processedContent = processedContent.replace(/```(\w*)\n([\s\S]*?)```/g, (m, lang, code) => {
    const highlighted = lang && lang !== 'text'
      ? hljs.highlight(code, { language: lang }).value
      : hljs.highlightAuto(code).value;
    return `<pre style="${buildStyleString(DEFAULT_STYLES.pre)}"><code>${highlighted}</code></pre>`;
  });

  // Markdown 转 HTML
  let html = marked.parse(processedContent, { breaks: true, gfm: true });

  // 应用样式
  html = html.replace(/<h1([^>]*)>/gi, `<h1 style="${buildStyleString(DEFAULT_STYLES.title)}"$1>`);
  html = html.replace(/<h2([^>]*)>/gi, `<h2 style="${buildStyleString(DEFAULT_STYLES.h2)}"$1>`);
  html = html.replace(/<h3([^>]*)>/gi, `<h3 style="${buildStyleString(DEFAULT_STYLES.h3)}"$1>`);
  html = html.replace(/<p([^>]*)>/gi, `<p style="${buildStyleString(DEFAULT_STYLES.p)}"$1>`);
  html = html.replace(/<strong([^>]*)>/gi, `<strong style="color:${DEFAULT_STYLES.strong.color};"$1>`);
  html = html.replace(/<blockquote>/gi, `<blockquote style="${buildStyleString(DEFAULT_STYLES.blockquote)}">`);
  html = html.replace(/<img\s/gi, `<img style="${buildStyleString(DEFAULT_STYLES.img)}" `);
  html = html.replace(/<table>/gi, `<table style="${buildStyleString(DEFAULT_STYLES.table)}">`);
  html = html.replace(/<th>/gi, `<th style="${buildStyleString(DEFAULT_STYLES.th)}">`);
  html = html.replace(/<td>/gi, `<td style="${buildStyleString(DEFAULT_STYLES.td)}">`);

  return { html, imageCount, firstImageMediaId };
}

// 生成默认封面图
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

  return await sharp(svgBuffer).png().toBuffer();
}

// 获取封面图
async function getCoverImage(firstImageMediaId, tokenManager) {
  if (firstImageMediaId) return firstImageMediaId;

  // 查找本地缩略图
  const paths = [
    path.resolve(process.cwd(), 'thumbnail.png'),
    path.resolve(process.cwd(), 'thumbnail.jpg'),
    path.resolve(__dirname, 'thumbnail.png'),
    path.resolve(__dirname, 'default-cover.png')
  ];

  for (const p of paths) {
    if (fs.existsSync(p)) {
      const result = await uploadImage(p, tokenManager);
      return result.media_id;
    }
  }

  // 生成默认封面
  const coverBuffer = await generateDefaultCoverImage();
  const tempPath = path.resolve(process.cwd(), '.temp-cover.png');
  fs.writeFileSync(tempPath, coverBuffer);

  try {
    const result = await uploadImage(tempPath, tokenManager);
    return result.media_id;
  } finally {
    fs.unlinkSync(tempPath);
  }
}

// 主函数
async function pushDraftFromFile(filePath, title, digest, sourceUrl) {
  const config = loadConfig();
  const tokenManager = new AccessTokenManager(config.appId, config.appSecret);

  // 读取文件
  const resolvedPath = path.isAbsolute(filePath) ? filePath : path.resolve(process.cwd(), filePath);
  if (!fs.existsSync(resolvedPath)) {
    throw new Error(`文件不存在：${resolvedPath}`);
  }

  const mdContent = fs.readFileSync(resolvedPath, 'utf-8');

  // 转换 Markdown
  const { html, imageCount, firstImageMediaId } = await markdownToHtml(mdContent, resolvedPath, tokenManager);

  // 获取封面图
  const thumbMediaId = await getCoverImage(firstImageMediaId, tokenManager);

  // 创建草稿
  const accessToken = await tokenManager.getAccessToken();
  const response = await axios.post(
    `${WECHAT_API_BASE}/cgi-bin/draft/add?access_token=${accessToken}`,
    {
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
    }
  );

  if (response.data.media_id) {
    return {
      success: true,
      media_id: response.data.media_id,
      message: '文章成功添加到草稿箱',
      html,
      imageCount,
      firstImageMediaId
    };
  }
  throw new Error(`创建草稿失败：${response.data.errmsg}`);
}

// CLI
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.length < 2) {
    console.log('Usage: node push-draft-file.js <filePath> <title> [digest] [sourceUrl]');
    process.exit(1);
  }

  const [filePath, title, digest, sourceUrl] = args;

  pushDraftFromFile(filePath, title, digest, sourceUrl)
    .then(result => {
      console.log('\n✅', result.message);
      console.log('📝 Media ID:', result.media_id);
      console.log('🖼️ 已处理图片:', result.imageCount, '张');
      if (result.firstImageMediaId) {
        console.log('📸 首图 Media ID:', result.firstImageMediaId);
      }
    })
    .catch(error => {
      console.error('\n❌ 失败:', error.message);
      process.exit(1);
    });
}

module.exports = { pushDraftFromFile };
