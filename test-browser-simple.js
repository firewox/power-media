#!/usr/bin/env node
/**
 * 简单测试 - 不使用持久化上下文
 */

const { firefox } = require('playwright');

async function testBrowser() {
  console.log('='.repeat(50));
  console.log('简单浏览器测试');
  console.log('='.repeat(50));
  
  let browser = null;
  
  try {
    console.log('\n启动 Firefox (headless)...');
    browser = await firefox.launch({
      headless: true,
    });
    
    console.log('✅ 浏览器启动成功！');
    
    const context = await browser.newContext();
    const page = await context.newPage();
    
    console.log('\n导航到小红书...');
    await page.goto('https://www.xiaohongshu.com/', {
      waitUntil: 'domcontentloaded',
      timeout: 30000,
    });
    
    console.log('✅ 页面加载成功！');
    console.log(`URL: ${page.url()}`);
    
    const title = await page.title();
    console.log(`标题: ${title}`);
    
    await page.waitForTimeout(2000);
    
    await context.close();
    await browser.close();
    
    console.log('\n' + '='.repeat(50));
    console.log('✅ 测试通过！');
    console.log('='.repeat(50));
    
  } catch (error) {
    console.error('\n❌ 测试失败:', error.message);
    if (browser) {
      await browser.close();
    }
    process.exit(1);
  }
}

testBrowser();
