#!/usr/bin/env node
/**
 * 上传图片到微信公众号素材库
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// 依赖检查
let axios;
let FormData;

try {
  axios = require('axios');
  FormData = require('form-data');
} catch (e) {
  console.error('❌ 缺少依赖包，请先运行: npm install axios form-data');
  process.exit(1);
}

const WECHAT_API_BASE = 'https://api.weixin.qq.com';

// 加载配置（支持多种方式）
function loadConfig() {
  // 方式 1：环境变量
  let appId = process.env.WECHAT_APP_ID;
  let appSecret = process.env.WECHAT_APP_SECRET;

  if (appId && appSecret) {
    return { appId, appSecret, source: 'environment' };
  }

  // 方式 2：.env 文件
  const envPaths = [
    path.resolve(process.cwd(), '.env'),
    path.resolve(__dirname, '.env'),
    path.resolve(__dirname, '../.env'),
    path.resolve(__dirname, '../../.env'),
    path.resolve(__dirname, '../../../.env')
  ];

  for (const envPath of envPaths) {
    if (fs.existsSync(envPath)) {
      const envContent = fs.readFileSync(envPath, 'utf-8');
      const envVars = {};
      envContent.split('\n').forEach(line => {
        const match = line.match(/^([^#=]+)=(.*)$/);
        if (match) {
          envVars[match[1].trim()] = match[2].trim().replace(/^["']|["']$/g, '');
        }
      });

      if (envVars.WECHAT_APP_ID && envVars.WECHAT_APP_SECRET) {
        return {
          appId: envVars.WECHAT_APP_ID,
          appSecret: envVars.WECHAT_APP_SECRET,
          source: 'env_file'
        };
      }
    }
  }

  // 方式 3：wechat-config.json
  const configPaths = [
    path.resolve(process.cwd(), 'wechat-config.json'),
    path.resolve(__dirname, 'wechat-config.json'),
    path.resolve(__dirname, '../wechat-config.json'),
    path.resolve(__dirname, '../../wechat-config.json'),
    path.resolve(__dirname, '../../../wechat-config.json'),
    path.resolve(os.homedir(), '.wechat-config.json')
  ];

  for (const configPath of configPaths) {
    if (fs.existsSync(configPath)) {
      try {
        const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
        const wechatConfig = config.wechat || config;

        if (wechatConfig.appId && wechatConfig.appSecret) {
          return {
            appId: wechatConfig.appId,
            appSecret: wechatConfig.appSecret,
            source: 'config_file'
          };
        }
      } catch (e) {
        console.error(`⚠️  配置文件格式错误: ${configPath}`);
      }
    }
  }

  throw new Error(
    '\n❌ 未找到微信公众号配置！\n\n' +
    '请设置环境变量或创建 .env / wechat-config.json 文件'
  );
}

// 获取 access_token
async function getAccessToken(config) {
  const response = await axios.get(`${WECHAT_API_BASE}/cgi-bin/token`, {
    params: {
      grant_type: 'client_credential',
      appid: config.appId,
      secret: config.appSecret
    },
    timeout: 30000
  });

  if (response.data.access_token) {
    return response.data.access_token;
  }

  throw new Error(`获取 access_token 失败: ${response.data.errmsg}`);
}

// 下载网络图片
async function downloadImage(url, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await axios.get(url, {
        responseType: 'arraybuffer',
        timeout: 30000,
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
      });

      const contentType = response.headers['content-type'];
      if (!contentType || !contentType.startsWith('image/')) {
        throw new Error('URL 返回的不是图片文件');
      }

      return Buffer.from(response.data);
    } catch (error) {
      if (i === retries - 1) {
        throw new Error(`下载图片失败: ${error.message}`);
      }
      console.log(`下载失败，第 ${i + 2} 次重试...`);
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
}

// 上传图片到微信
async function uploadImage(imageSource, isTemporary = false) {
  const config = loadConfig();
  console.log('正在获取 access_token...');
  const accessToken = await getAccessToken(config);

  console.log(`正在${isTemporary ? '下载' : '读取'}图片...`);
  let imageBuffer;
  let filename;

  // 判断是 URL 还是本地文件
  if (imageSource.startsWith('http://') || imageSource.startsWith('https://')) {
    imageBuffer = await downloadImage(imageSource);
    filename = path.basename(new URL(imageSource).pathname) || 'image.jpg';
  } else {
    // 本地文件
    const localPath = path.resolve(imageSource);
    if (!fs.existsSync(localPath)) {
      throw new Error(`文件不存在: ${localPath}`);
    }
    imageBuffer = fs.readFileSync(localPath);
    filename = path.basename(localPath);
  }

  // 检查文件大小（2MB限制）
  if (imageBuffer.length > 2 * 1024 * 1024) {
    throw new Error('图片大小超过 2MB 限制');
  }

  console.log(`图片大小: ${(imageBuffer.length / 1024).toFixed(2)} KB`);

  // 构建表单
  const form = new FormData();
  form.append('media', imageBuffer, {
    filename: filename,
    contentType: 'image/jpeg'
  });

  console.log(`正在上传${isTemporary ? '临时' : '永久'}素材...`);

  // 选择 API 端点
  const endpoint = isTemporary
    ? `/cgi-bin/media/upload?access_token=${accessToken}&type=image`
    : `/cgi-bin/material/add_material?access_token=${accessToken}&type=image`;

  const response = await axios.post(`${WECHAT_API_BASE}${endpoint}`, form, {
    headers: form.getHeaders(),
    timeout: 60000
  });

  if (response.data.errcode) {
    throw new Error(`上传失败: ${response.data.errmsg} (错误码: ${response.data.errcode})`);
  }

  return {
    success: true,
    mediaId: response.data.media_id || response.data.url,
    url: response.data.url,
    type: 'image',
    createdAt: response.data.created_at || Date.now()
  };
}

// CLI
if (require.main === module) {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log('用法: node upload-image.js <图片URL或路径> [--temporary]');
    console.log('');
    console.log('选项:');
    console.log('  --temporary  上传为临时素材（3天有效）');
    console.log('');
    console.log('示例:');
    console.log('  node upload-image.js https://example.com/image.jpg');
    console.log('  node upload-image.js ./photo.png');
    console.log('  node upload-image.js https://example.com/tmp.gif --temporary');
    process.exit(0);
  }

  const imageSource = args[0];
  const isTemporary = args.includes('--temporary');

  uploadImage(imageSource, isTemporary)
    .then(result => {
      console.log('\n✅ 图片上传成功');
      console.log('='.repeat(50));
      console.log(`Media ID: ${result.mediaId}`);
      if (result.url) {
        console.log(`URL: ${result.url}`);
      }
      console.log(`类型: ${isTemporary ? '临时素材' : '永久素材'}`);
      console.log('');
    })
    .catch(error => {
      console.error('\n❌ 上传失败');
      console.error('='.repeat(50));
      console.error('错误:', error.message);
      process.exit(1);
    });
}

module.exports = { uploadImage };
