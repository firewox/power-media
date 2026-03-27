/**
 * 公共工具函数模块
 */

const fs = require('fs');
const path = require('path');

const LOG_PREFIX = '[XHS]';

const LogLevel = {
  DEBUG: 'DEBUG',
  INFO: 'INFO',
  WARN: 'WARN',
  ERROR: 'ERROR',
};

function log(level, message, ...args) {
  const timestamp = new Date().toISOString();
  const formatted = `${timestamp} ${LOG_PREFIX} [${level}] ${message}`;
  
  switch (level) {
    case LogLevel.ERROR:
      console.error(formatted, ...args);
      break;
    case LogLevel.WARN:
      console.warn(formatted, ...args);
      break;
    default:
      console.log(formatted, ...args);
  }
}

const logger = {
  debug: (msg, ...args) => log(LogLevel.DEBUG, msg, ...args),
  info: (msg, ...args) => log(LogLevel.INFO, msg, ...args),
  warn: (msg, ...args) => log(LogLevel.WARN, msg, ...args),
  error: (msg, ...args) => log(LogLevel.ERROR, msg, ...args),
};

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function randomSleep(min = 500, max = 2000) {
  const delay = Math.floor(Math.random() * (max - min + 1)) + min;
  logger.debug(`随机延迟 ${delay}ms`);
  return sleep(delay);
}

function validateParams(params, requiredKeys) {
  const missing = [];
  
  for (const key of requiredKeys) {
    if (params[key] === undefined || params[key] === null || params[key] === '') {
      missing.push(key);
    }
  }
  
  if (missing.length > 0) {
    throw new Error(`缺少必需参数: ${missing.join(', ')}`);
  }
  
  return true;
}

function ensureDir(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

function formatDate(date = new Date()) {
  return date.toISOString().replace(/[:.]/g, '-').slice(0, 19);
}

function generateId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
}

function parseCookieString(cookieString) {
  const cookies = {};
  
  if (!cookieString) return cookies;
  
  const pairs = cookieString.split(';');
  for (const pair of pairs) {
    const [key, ...valueParts] = pair.trim().split('=');
    if (key && valueParts.length > 0) {
      cookies[key.trim()] = valueParts.join('=').trim();
    }
  }
  
  return cookies;
}

function cookiesToString(cookies) {
  if (!cookies || typeof cookies !== 'object') return '';
  
  return Object.entries(cookies)
    .map(([key, value]) => `${key}=${value}`)
    .join('; ');
}

function extractUrlParams(url) {
  const params = {};
  
  try {
    const urlObj = new URL(url);
    for (const [key, value] of urlObj.searchParams) {
      params[key] = value;
    }
  } catch (e) {
    logger.warn('URL 解析失败:', e.message);
  }
  
  return params;
}

function truncate(text, maxLength = 100) {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

class RetryableError extends Error {
  constructor(message, originalError = null) {
    super(message);
    this.name = 'RetryableError';
    this.originalError = originalError;
  }
}

async function retry(fn, options = {}) {
  const {
    maxRetries = 3,
    delay = 1000,
    backoff = 2,
    onRetry = null,
  } = options;
  
  let lastError;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      
      if (attempt < maxRetries) {
        const waitTime = delay * Math.pow(backoff, attempt - 1);
        logger.warn(`尝试 ${attempt}/${maxRetries} 失败，${waitTime}ms 后重试:`, error.message);
        
        if (onRetry) {
          onRetry(attempt, error);
        }
        
        await sleep(waitTime);
      }
    }
  }
  
  throw lastError;
}

function waitFor(conditionFn, options = {}) {
  const {
    timeout = 30000,
    interval = 500,
    timeoutMessage = '等待超时',
  } = options;
  
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    
    const check = async () => {
      try {
        const result = await conditionFn();
        if (result) {
          resolve(result);
        } else if (Date.now() - startTime >= timeout) {
          reject(new Error(timeoutMessage));
        } else {
          setTimeout(check, interval);
        }
      } catch (error) {
        if (Date.now() - startTime >= timeout) {
          reject(error);
        } else {
          setTimeout(check, interval);
        }
      }
    };
    
    check();
  });
}

module.exports = {
  logger,
  LogLevel,
  log,
  sleep,
  randomSleep,
  validateParams,
  ensureDir,
  formatDate,
  generateId,
  parseCookieString,
  cookiesToString,
  extractUrlParams,
  truncate,
  RetryableError,
  retry,
  waitFor,
};
