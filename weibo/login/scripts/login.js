#!/usr/bin/env node

const { launchBrowser, createContext, saveCookies, waitForQRCodeScan, WEIBO_URL } = require('../../lib/weibo.js');

async function main() {
  console.log('正在打开微博登录页面...\n');
  
  let browser;
  try {
    browser = await launchBrowser(false);
<<<<<<< HEAD
    const context = await browser.newContext({
      viewport: { width: 1280, height: 720 },
    });
=======
    const context = await createContext(browser);
>>>>>>> weibo-dev
    const page = await context.newPage();
    
    await page.goto(WEIBO_URL, { waitUntil: 'networkidle' });
    
    const qrTab = await page.$('a[action-type="qrcode_tab"]');
    if (qrTab) {
      await qrTab.click();
      await page.waitForTimeout(1000);
    }
    
    console.log('请使用微博 APP 扫描二维码登录...\n');
    
    const result = await waitForQRCodeScan(page, 120000);
    
    if (result.success) {
      await saveCookies(context);
      console.log('\n登录成功！');
      console.log(`用户名: ${result.userName}`);
      console.log('Cookie 已保存');
      process.exit(0);
    } else {
      console.error('\n登录失败:', result.error);
      process.exit(1);
    }
  } catch (error) {
    console.error('登录失败:', error.message);
    process.exit(1);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

main();
