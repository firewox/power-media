#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const os = require('os');

const SKILL_ROOT = path.resolve(__dirname, '..');
const PROJECT_ROOT = path.resolve(SKILL_ROOT, '..', '..', '..');
const WECHAT_API_BASE = 'https://api.weixin.qq.com';

const sharedTokenCache = new Map();

function resolveConfigPaths() {
  return {
    configFiles: [
      path.join(SKILL_ROOT, 'wechat-config.json'),
      path.join(PROJECT_ROOT, 'wechat-config.json'),
      path.join(process.cwd(), 'wechat-config.json'),
      path.join(os.homedir(), '.wechat-config.json')
    ],
    envFiles: [
      path.join(PROJECT_ROOT, '.env'),
      path.join(process.cwd(), '.env'),
      path.join(SKILL_ROOT, '.env')
    ]
  };
}

function parseEnvFile(filePath) {
  const envVars = {};
  const envContent = fs.readFileSync(filePath, 'utf-8');
  for (const rawLine of envContent.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith('#')) {
      continue;
    }
    const equalIndex = line.indexOf('=');
    if (equalIndex === -1) {
      continue;
    }
    const key = line.slice(0, equalIndex).trim();
    const value = line.slice(equalIndex + 1).trim().replace(/^["']|["']$/g, '');
    envVars[key] = value;
  }
  return envVars;
}

function normalizeConfig(input, source) {
  if (!input || typeof input !== 'object') {
    return null;
  }

  const nested = input.wechat && typeof input.wechat === 'object' ? input.wechat : input;
  const appId = nested.WECHAT_APP_ID || nested.appId;
  const appSecret = nested.WECHAT_APP_SECRET || nested.appSecret;

  if (!appId || !appSecret) {
    return null;
  }

  return {
    appId,
    appSecret,
    defaultAuthor: nested.WECHAT_DEFAULT_AUTHOR || nested.defaultAuthor || '',
    needOpenComment: String(nested.WECHAT_NEED_OPEN_COMMENT || nested.needOpenComment || '').toLowerCase() === 'true',
    onlyFansCanComment: String(nested.WECHAT_ONLY_FANS_CAN_COMMENT || nested.onlyFansCanComment || '').toLowerCase() === 'true',
    source
  };
}

function loadConfig() {
  const { configFiles, envFiles } = resolveConfigPaths();

  for (const configPath of configFiles) {
    if (!fs.existsSync(configPath)) {
      continue;
    }
    try {
      const parsed = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
      const normalized = normalizeConfig(parsed, `config:${configPath}`);
      if (normalized) {
        return normalized;
      }
    } catch (error) {
      throw createStageError('load-config', `配置文件解析失败: ${configPath}`, {
        configPath,
        rawError: error.message
      });
    }
  }

  for (const envPath of envFiles) {
    if (!fs.existsSync(envPath)) {
      continue;
    }
    const normalized = normalizeConfig(parseEnvFile(envPath), `env-file:${envPath}`);
    if (normalized) {
      return normalized;
    }
  }

  const normalizedEnv = normalizeConfig(process.env, 'environment');
  if (normalizedEnv) {
    return normalizedEnv;
  }

  throw createStageError('load-config', '未找到微信公众号配置', {
    searchedConfigFiles: configFiles,
    searchedEnvFiles: envFiles,
    requiredKeys: ['WECHAT_APP_ID', 'WECHAT_APP_SECRET']
  });
}

function createStageError(stage, message, extra = {}) {
  const error = new Error(message);
  error.stage = stage;
  Object.assign(error, extra);
  return error;
}

function summarizeAxiosError(error) {
  if (!error || typeof error !== 'object') {
    return {};
  }
  const response = error.response;
  if (!response) {
    return {
      code: error.code,
      rawError: error.message || String(error)
    };
  }
  const data = response.data || {};
  const summary = {
    httpStatus: response.status,
    errcode: data.errcode,
    errmsg: data.errmsg
  };
  if (typeof data === 'string') {
    summary.responseBody = data;
  } else {
    summary.responseBody = data;
  }
  return summary;
}

function wrapError(stage, message, error, extra = {}) {
  const merged = {
    ...extra,
    ...summarizeAxiosError(error)
  };
  if (error && !merged.rawError) {
    merged.rawError = error.message || String(error);
  }
  return createStageError(stage, message, merged);
}

function formatStageError(error) {
  if (!error) {
    return {
      success: false,
      stage: 'unknown',
      message: '未知错误',
      raw_error: 'Unknown error'
    };
  }
  return {
    success: false,
    stage: error.stage || 'unknown',
    message: error.message || '未知错误',
    errcode: error.errcode,
    http_status: error.httpStatus,
    raw_error: error.rawError,
    response_body: error.responseBody
  };
}

function hasJsonFlag(args) {
  return Array.isArray(args) && args.includes('--json');
}

function printResult(result, asJson = false) {
  if (asJson) {
    console.log(JSON.stringify(result, null, 2));
    return;
  }
  if (result.success) {
    console.log(result.message || '成功');
    return;
  }
  console.error(result.message || '失败');
}

function exitWithError(error, asJson = false) {
  const result = formatStageError(error);
  if (asJson) {
    console.error(JSON.stringify(result, null, 2));
  } else {
    console.error(`\n❌ [${result.stage}] ${result.message}`);
    if (result.errcode !== undefined) {
      console.error(`错误码: ${result.errcode}`);
    }
    if (result.http_status !== undefined) {
      console.error(`HTTP 状态: ${result.http_status}`);
    }
    if (result.raw_error) {
      console.error(`原始错误: ${result.raw_error}`);
    }
  }
  process.exit(1);
}

class AccessTokenManager {
  constructor(axios, appId, appSecret) {
    this.axios = axios;
    this.appId = appId;
    this.appSecret = appSecret;
    this.cacheKey = `${appId}:${appSecret}`;
  }

  async getAccessToken() {
    const now = Date.now();
    const cached = sharedTokenCache.get(this.cacheKey);
    if (cached && now < cached.expireTime) {
      return cached.token;
    }

    let response;
    try {
      response = await this.axios.get(`${WECHAT_API_BASE}/cgi-bin/token`, {
        params: {
          grant_type: 'client_credential',
          appid: this.appId,
          secret: this.appSecret
        },
        timeout: 30000
      });
    } catch (error) {
      throw wrapError('get-access-token', '获取 access_token 请求失败', error);
    }

    if (response.data && response.data.access_token) {
      sharedTokenCache.set(this.cacheKey, {
        token: response.data.access_token,
        expireTime: now + (response.data.expires_in - 300) * 1000
      });
      return response.data.access_token;
    }

    throw createStageError('get-access-token', '获取 access_token 失败', {
      errcode: response.data?.errcode,
      rawError: response.data?.errmsg,
      responseBody: response.data
    });
  }
}

function formatTime(timestamp) {
  if (!timestamp) {
    return '';
  }
  return new Date(timestamp * 1000).toLocaleString('zh-CN');
}

function resolveImageSource(imageSource, baseDir) {
  if (/^https?:\/\//i.test(imageSource)) {
    return imageSource;
  }
  if (path.isAbsolute(imageSource)) {
    return imageSource;
  }
  return path.resolve(baseDir || process.cwd(), imageSource);
}

function detectContentType(filename) {
  const ext = path.extname(filename).toLowerCase();
  if (ext === '.png') return 'image/png';
  if (ext === '.gif') return 'image/gif';
  if (ext === '.bmp') return 'image/bmp';
  if (ext === '.webp') return 'image/webp';
  return 'image/jpeg';
}

async function downloadImage(axios, imageUrl) {
  const maxRetries = 3;
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await axios.get(imageUrl, {
        responseType: 'arraybuffer',
        timeout: 30000,
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
      });
      return {
        data: Buffer.from(response.data),
        contentType: response.headers['content-type'] || 'image/jpeg',
        filename: path.basename(new URL(imageUrl).pathname) || 'image.jpg'
      };
    } catch (error) {
      if (attempt === maxRetries) {
        throw wrapError('download-image', `下载图片失败: ${imageUrl}`, error, { imageUrl });
      }
      await new Promise(resolve => setTimeout(resolve, attempt * 1000));
    }
  }
}

async function readImageSource(fsModule, axios, imageSource, baseDir) {
  const resolved = resolveImageSource(imageSource, baseDir);
  if (/^https?:\/\//i.test(resolved)) {
    return downloadImage(axios, resolved);
  }

  if (!fsModule.existsSync(resolved)) {
    throw createStageError('read-image', `图片文件不存在: ${resolved}`, {
      imageSource,
      resolvedPath: resolved
    });
  }

  return {
    data: fsModule.readFileSync(resolved),
    contentType: detectContentType(resolved),
    filename: path.basename(resolved),
    resolvedPath: resolved
  };
}

module.exports = {
  AccessTokenManager,
  PROJECT_ROOT,
  SKILL_ROOT,
  WECHAT_API_BASE,
  createStageError,
  detectContentType,
  exitWithError,
  formatStageError,
  formatTime,
  hasJsonFlag,
  loadConfig,
  printResult,
  readImageSource,
  resolveConfigPaths,
  resolveImageSource,
  summarizeAxiosError,
  wrapError
};
