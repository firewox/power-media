#!/usr/bin/env node
/**
 * 测试浏览器启动
 */

const path = require('path');
const { BrowserManager, closeAll } = require('./rednote/lib/browser');

const DATA_PATH = path.join(__dirname, 'test-data');

async function testBrowser() {
  console.log('='.repeat(50));
  console.log('测试浏览器启动');
  console.log('='.repeat(50));
  
  const browserManager = new BrowserManager(DATA_PATH, {
    browserType: 'firefox',
    headless: true,  // WSL 环境使用 headless 模式
  });
  
  try {
    console.log('\n正在启动浏览器...');
    const page = await browserManager.getPage();
    
    console.log('✅ 浏览器启动成功！');
    
    console.log('\n导航到小红书首页...');
    await page.goto('https://www.xiaohongshu.com/', {
      waitUntil: 'domcontentloaded',
      timeout: 30000,
    });
    
    console.log('✅ 页面加载成功！');
    console.log(`当前 URL: ${page.url()}`);
    
    await page.waitForTimeout(5000);
    
    console.log('\n测试完成，关闭浏览器...');
    await closeAll();
    
    console.log('\n' + '='.repeat(50));
    console.log('✅ 浏览器测试通过！');
    console.log('='.repeat(50));
    
  } catch (error) {
    console.error('\n❌ 测试失败:', error.message);
    await closeAll();
    process.exit(1);
  }
}

testBrowser();
