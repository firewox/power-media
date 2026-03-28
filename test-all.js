#!/usr/bin/env node
/**
 * 完整测试脚本
 */

const path = require('path');
const { BrowserManager, closeAll } = require('./rednote/lib/browser');

const DATA_PATH = path.join(__dirname, 'test-data');

async function testBrowser() {
  console.log('='.repeat(60));
  console.log('RedNote Skills 测试');
  console.log('='.repeat(60));
  
  const browserManager = new BrowserManager(DATA_PATH, {
    browserType: 'firefox',
    headless: true,
    persistent: false,  // WSL 环境使用非持久化模式
  });
  
  try {
    console.log('\n[1/3] 启动浏览器...');
    const page = await browserManager.getPage();
    console.log('✅ 浏览器启动成功！');
    
    console.log('\n[2/3] 访问小红书首页...');
    await page.goto('https://www.xiaohongshu.com/', {
      waitUntil: 'domcontentloaded',
      timeout: 30000,
    });
    
    const title = await page.title();
    console.log(`✅ 页面加载成功！标题: ${title}`);
    
    console.log('\n[3/3] 测试 Cookie 管理...');
    const cookies = await page.context().cookies();
    console.log(`✅ 当前 Cookie 数量: ${cookies.length}`);
    
    await page.waitForTimeout(2000);
    
    console.log('\n关闭浏览器...');
    await closeAll();
    
    console.log('\n' + '='.repeat(60));
    console.log('✅ 所有测试通过！');
    console.log('='.repeat(60));
    
    return true;
    
  } catch (error) {
    console.error('\n❌ 测试失败:', error.message);
    await closeAll();
    return false;
  }
}

async function testSkillsImport() {
  console.log('\n测试 Skills 模块导入...\n');
  
  const skills = [
    'check-login',
    'get-qrcode', 
    'logout',
    'publish-note',
    'publish-video',
    'search',
    'get-feed',
    'get-feeds',
    'get-profile',
    'like',
    'favorite',
    'comment',
    'reply',
  ];
  
  let passed = 0;
  let failed = 0;
  
  for (const skill of skills) {
    try {
      const skillPath = path.join(__dirname, 'rednote', skill, 'scripts', `${skill}.js`);
      require(skillPath);
      console.log(`✅ ${skill}`);
      passed++;
    } catch (error) {
      console.log(`❌ ${skill}: ${error.message}`);
      failed++;
    }
  }
  
  console.log(`\n模块导入: ${passed}/${skills.length} 通过`);
  return failed === 0;
}

async function main() {
  const importOk = testSkillsImport();
  const browserOk = await testBrowser();
  
  console.log('\n' + '='.repeat(60));
  console.log('测试汇总');
  console.log('='.repeat(60));
  console.log(`模块导入测试: ${importOk ? '✅ 通过' : '❌ 失败'}`);
  console.log(`浏览器测试: ${browserOk ? '✅ 通过' : '❌ 失败'}`);
  
  process.exit(importOk && browserOk ? 0 : 1);
}

main();
