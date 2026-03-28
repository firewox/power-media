#!/usr/bin/env node

const path = require('path');

const libPath = path.join(__dirname, '..', '..', 'lib');
const { BrowserManager, getBrowserManager, closeAll } = require(path.join(libPath, 'browser'));
const { CookieManager } = require(path.join(libPath, 'cookie'));
const { logger, randomSleep } = require(path.join(libPath, 'utils'));

const DATA_PATH = process.env.XHS_DATA_PATH || path.join(__dirname, '..', '..', 'data');
const CREATOR_URL = 'https://creator.xiaohongshu.com/';

const LOGIN_SELECTORS = {
  userInfo: '.user-info',
  userName: '.user-name',
  avatar: '.avatar',
  loginButton: '.login-btn',
};

async function checkLogin(options = {}) {
  const dataPath = options.dataPath || DATA_PATH;
  
  logger.info('检查登录状态...');
  logger.info(`数据路径: ${dataPath}`);
  
  const browserManager = getBrowserManager(dataPath, { headless: false });
  const cookieManager = new CookieManager(dataPath);
  
  try {
    const page = await browserManager.getPage();
    
    logger.info('访问创作者中心...');
    await page.goto(CREATOR_URL, { waitUntil: 'domcontentloaded' });
    
    await randomSleep(2000, 3000);
    
    const userInfo = await page.$(LOGIN_SELECTORS.userInfo);
    
    if (userInfo) {
      logger.info('检测到用户信息，已登录');
      
      let username = '';
      let userId = '';
      
      try {
        const userNameEl = await page.$(LOGIN_SELECTORS.userName);
        if (userNameEl) {
          username = await userNameEl.textContent() || '';
          username = username.trim();
        }
        
        const currentUrl = page.url();
        const urlMatch = currentUrl.match(/\/user\/profile\/(\w+)/);
        if (urlMatch) {
          userId = urlMatch[1];
        }
        
        const pageContent = await page.content();
        const idMatch = pageContent.match(/"userId"\s*:\s*"(\w+)"/);
        if (idMatch) {
          userId = idMatch[1];
        }
      } catch (e) {
        logger.warn('获取用户信息失败:', e.message);
      }
      
      await cookieManager.saveLoginState({
        isLoggedIn: true,
        username,
        userId,
      });
      
      return {
        success: true,
        isLoggedIn: true,
        username,
        userId,
        message: '已登录',
      };
    }
    
    const loginButton = await page.$(LOGIN_SELECTORS.loginButton);
    if (loginButton) {
      logger.info('检测到登录按钮，未登录');
      
      return {
        success: true,
        isLoggedIn: false,
        message: '未登录，请先执行 get-qrcode 获取登录二维码',
      };
    }
    
    await randomSleep(1000, 2000);
    
    const qrCode = await page.$('.qrcode-box, .login-qrcode, [class*="qr"]');
    if (qrCode) {
      logger.info('检测到二维码登录页面，未登录');
      
      return {
        success: true,
        isLoggedIn: false,
        message: '未登录，请先执行 get-qrcode 获取登录二维码',
      };
    }
    
    logger.warn('无法确定登录状态');
    
    return {
      success: true,
      isLoggedIn: false,
      message: '无法确定登录状态，建议重新登录',
    };
    
  } catch (error) {
    logger.error('检查登录状态失败:', error.message);
    
    return {
      success: false,
      isLoggedIn: false,
      error: error.message,
      message: '检查登录状态失败',
    };
  }
}

async function main() {
  const result = await checkLogin();
  
  console.log('\n' + '='.repeat(50));
  
  if (result.success) {
    if (result.isLoggedIn) {
      console.log('✅ 已登录');
      console.log(`用户名: ${result.username || '未知'}`);
      console.log(`用户ID: ${result.userId || '未知'}`);
    } else {
      console.log('❌ 未登录');
      console.log(result.message);
    }
  } else {
    console.log('❌ 检查失败');
    console.log(`错误: ${result.error}`);
  }
  
  console.log('='.repeat(50));
  
  await closeAll();
  
  process.exit(result.success && result.isLoggedIn ? 0 : 1);
}

if (require.main === module) {
  main();
}

module.exports = { checkLogin };
