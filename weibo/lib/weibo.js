const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const COOKIE_FILE = path.join(__dirname, '..', '.cookies.json');
const WEIBO_URL = 'https://weibo.com';

async function launchBrowser(headless = false) {
  return await chromium.launch({
    headless,
    args: ['--disable-blink-features=AutomationControlled'],
  });
}

async function createContext(browser) {
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  });

  if (fs.existsSync(COOKIE_FILE)) {
    const cookies = JSON.parse(fs.readFileSync(COOKIE_FILE, 'utf-8'));
    await context.addCookies(cookies);
  }

  return context;
}

async function saveCookies(context) {
  const cookies = await context.cookies();
  fs.writeFileSync(COOKIE_FILE, JSON.stringify(cookies, null, 2));
}

async function clearCookies() {
  if (fs.existsSync(COOKIE_FILE)) {
    fs.unlinkSync(COOKIE_FILE);
  }
}

async function checkLoginStatus(page) {
  await page.goto(WEIBO_URL, { waitUntil: 'networkidle' });
  
  const loginButton = await page.$('a[href="//weibo.com/login.php"]');
  const userName = await page.$('.user-name');
  
  if (userName) {
    const name = await userName.textContent();
    return { loggedIn: true, userName: name.trim() };
  }
  
  return { loggedIn: false };
}

async function waitForQRCodeScan(page, timeout = 120000) {
  console.log('请使用微博 APP 扫描二维码登录...');
  
  const startTime = Date.now();
  while (Date.now() - startTime < timeout) {
    await page.waitForTimeout(2000);
    
    const userName = await page.$('.user-name');
    if (userName) {
      const name = await userName.textContent();
      return { success: true, userName: name.trim() };
    }
    
    const error = await page.$('.login-error');
    if (error) {
      const msg = await error.textContent();
      return { success: false, error: msg };
    }
  }
  
  return { success: false, error: '二维码扫描超时' };
}

async function postText(page, text) {
  if (text.length > 140) {
    throw new Error('微博内容不能超过 140 个字符');
  }

  await page.goto('https://weibo.com/u/0/home', { waitUntil: 'networkidle' });
  
  const textarea = await page.waitForSelector('textarea[node-type="textEl"]', { timeout: 10000 });
  await textarea.fill(text);
  
  const sendButton = await page.$('a[node-type="sendBtn"]');
  if (!sendButton) {
    throw new Error('未找到发送按钮');
  }
  
  await sendButton.click();
  
  await page.waitForTimeout(2000);
  
  const successTip = await page.$('.W_tips_success');
  if (successTip) {
    const msg = await successTip.textContent();
    return { success: true, message: msg };
  }
  
  const errorTip = await page.$('.W_tips_error');
  if (errorTip) {
    const msg = await errorTip.textContent();
    return { success: false, error: msg };
  }
  
  return { success: true };
}

async function postWithImage(page, text, imagePath) {
  if (!fs.existsSync(imagePath)) {
    throw new Error(`图片文件不存在: ${imagePath}`);
  }

  if (text.length > 140) {
    throw new Error('微博内容不能超过 140 个字符');
  }

  await page.goto('https://weibo.com/u/0/home', { waitUntil: 'networkidle' });
  
  const textarea = await page.waitForSelector('textarea[node-type="textEl"]', { timeout: 10000 });
  await textarea.fill(text);
  
  const uploadInput = await page.$('input[node-type="uploadInput"]');
  if (!uploadInput) {
    throw new Error('未找到图片上传控件');
  }
  
  await uploadInput.setInputFiles(imagePath);
  
  await page.waitForTimeout(3000);
  
  const sendButton = await page.$('a[node-type="sendBtn"]');
  if (!sendButton) {
    throw new Error('未找到发送按钮');
  }
  
  await sendButton.click();
  
  await page.waitForTimeout(2000);
  
  const successTip = await page.$('.W_tips_success');
  if (successTip) {
    const msg = await successTip.textContent();
    return { success: true, message: msg };
  }
  
  const errorTip = await page.$('.W_tips_error');
  if (errorTip) {
    const msg = await errorTip.textContent();
    return { success: false, error: msg };
  }
  
  return { success: true };
}

module.exports = {
  launchBrowser,
  createContext,
  saveCookies,
  clearCookies,
  checkLoginStatus,
  waitForQRCodeScan,
  postText,
  postWithImage,
  COOKIE_FILE,
  WEIBO_URL,
};
