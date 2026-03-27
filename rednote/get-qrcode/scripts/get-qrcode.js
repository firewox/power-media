#!/usr/bin/env node

const path = require('path');
const fs = require('fs');

const libPath = path.join(__dirname, '..', 'lib');
const { BrowserManager, getBrowserManager, closeAll } = require(path.join(libPath, 'browser'));
const { CookieManager, syncCookiesFromContext } = require(path.join(libPath, 'cookie'));
const { logger, randomSleep, formatDate } = require(path.join(libPath, 'utils'));

const DATA_PATH = process.env.XHS_DATA_PATH || path.join(__dirname, '..', '..', 'data');
const CREATOR_URL = 'https://creator.xiaohongshu.com/';
const LOGIN_URL = 'https://creator.xiaohongshu.com/login';

const SELECTORS = {
  qrcode: '.qrcode-box img, .login-qrcode img, [class*="qr"] img',
  qrcodeCanvas: '.qrcode-box canvas, .login-qrcode canvas',
  userInfo: '.user-info',
  userName: '.user-name',
};

async function getQrcode(options = {}) {
  const dataPath = options.dataPath || DATA_PATH;
  const savePath = options.savePath || path.join(dataPath, 'qrcode.png');
  
  logger.info('获取登录二维码...');
  logger.info(`数据路径: ${dataPath}`);
  
  const browserManager = getBrowserManager(dataPath, { headless: false });
  const cookieManager = new CookieManager(dataPath);
  
  cookieManager.ensureDataDir();
  
  try {
    const page = await browserManager.getPage();
    
    logger.info('访问登录页面...');
    await page.goto(CREATOR_URL, { waitUntil: 'domcontentloaded' });
    
    await randomSleep(2000, 3000);
    
    const qrcodeImg = await page.$(SELECTORS.qrcode);
    if (qrcodeImg) {
      logger.info('找到二维码图片');
      
      await qrcodeImg.screenshot({ path: savePath });
      logger.info(`二维码已保存: ${savePath}`);
      
      return {
        success: true,
        qrcodePath: savePath,
        message: '请扫描二维码登录',
        deadline: new Date(Date.now() + 180000).toISOString(),
        browserManager,
        page,
      };
    }
    
    const qrcodeCanvas = await page.$(SELECTORS.qrcodeCanvas);
    if (qrcodeCanvas) {
      logger.info('找到二维码 Canvas');
      
      const buffer = await qrcodeCanvas.screenshot();
      fs.writeFileSync(savePath, buffer);
      logger.info(`二维码已保存: ${savePath}`);
      
      return {
        success: true,
        qrcodePath: savePath,
        message: '请扫描二维码登录',
        deadline: new Date(Date.now() + 180000).toISOString(),
        browserManager,
        page,
      };
    }
    
    const pageUrl = page.url();
    if (pageUrl.includes('/creator.xiaohongshu.com') && !pageUrl.includes('/login')) {
      logger.info('已处于登录状态');
      
      return {
        success: true,
        isLoggedIn: true,
        message: '已登录，无需获取二维码',
        browserManager,
        page,
      };
    }
    
    logger.warn('未找到二维码元素，尝试截取整个页面');
    
    const fullSavePath = path.join(dataPath, 'login-page.png');
    await page.screenshot({ path: fullSavePath, fullPage: false });
    
    return {
      success: true,
      qrcodePath: fullSavePath,
      message: '请查看登录页面截图',
      deadline: new Date(Date.now() + 180000).toISOString(),
      browserManager,
      page,
    };
    
  } catch (error) {
    logger.error('获取二维码失败:', error.message);
    
    return {
      success: false,
      error: error.message,
    };
  }
}

async function waitForLogin(options = {}) {
  const timeout = (options.timeout || 120) * 1000;
  const dataPath = options.dataPath || DATA_PATH;
  const cookieManager = new CookieManager(dataPath);
  
  logger.info('等待扫码登录...');
  logger.info(`超时时间: ${timeout / 1000} 秒`);
  
  const result = await getQrcode(options);
  
  if (!result.success) {
    return result;
  }
  
  if (result.isLoggedIn) {
    return result;
  }
  
  console.log('\n' + '='.repeat(50));
  console.log('📱 请用小红书 App 扫描二维码登录');
  console.log(`   二维码路径: ${result.qrcodePath}`);
  console.log(`   有效期: 3 分钟`);
  console.log('='.repeat(50) + '\n');
  
  const page = result.page;
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeout) {
    await randomSleep(2000, 3000);
    
    const currentUrl = page.url();
    
    if (currentUrl.includes('/creator.xiaohongshu.com') && !currentUrl.includes('/login')) {
      logger.info('检测到页面跳转，登录成功');
      
      await randomSleep(2000, 3000);
      
      const userInfo = await page.$(SELECTORS.userInfo);
      if (userInfo) {
        let username = '';
        let userId = '';
        
        try {
          const userNameEl = await page.$(SELECTORS.userName);
          if (userNameEl) {
            username = await userNameEl.textContent() || '';
            username = username.trim();
          }
        } catch (e) {
          logger.warn('获取用户名失败:', e.message);
        }
        
        await syncCookiesFromContext(result.browserManager.getContext(), cookieManager);
        
        await cookieManager.saveLoginState({
          isLoggedIn: true,
          username,
          userId,
        });
        
        console.log('\n' + '='.repeat(50));
        console.log('✅ 登录成功！');
        console.log(`用户名: ${username || '未知'}`);
        console.log('='.repeat(50) + '\n');
        
        return {
          success: true,
          isLoggedIn: true,
          username,
          userId,
          message: '登录成功',
        };
      }
    }
    
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    if (elapsed % 10 === 0) {
      logger.info(`等待扫码登录... (${elapsed}秒)`);
    }
  }
  
  logger.warn('等待登录超时');
  
  return {
    success: false,
    isLoggedIn: false,
    message: '等待登录超时，请重新获取二维码',
  };
}

async function main() {
  const args = process.argv.slice(2);
  const noWait = args.includes('--no-wait');
  
  let result;
  
  if (noWait) {
    result = await getQrcode();
    
    if (result.success) {
      console.log('\n' + '='.repeat(50));
      console.log('📱 登录二维码');
      console.log(`   路径: ${result.qrcodePath}`);
      console.log(`   有效期: 3 分钟`);
      console.log('='.repeat(50) + '\n');
    }
  } else {
    result = await waitForLogin();
  }
  
  if (!result.success) {
    console.log('\n❌ 失败:', result.message || result.error);
    process.exit(1);
  }
  
  process.exit(0);
}

if (require.main === module) {
  main().catch(error => {
    console.error('执行失败:', error);
    process.exit(1);
  });
}

module.exports = { getQrcode, waitForLogin };
