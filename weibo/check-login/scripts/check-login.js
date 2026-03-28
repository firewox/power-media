#!/usr/bin/env node

const { launchBrowser, createContext, checkLoginStatus } = require('../../lib/weibo.js');

async function main() {
  console.log('正在检查微博登录状态...\n');
  
  let browser;
  try {
    browser = await launchBrowser(true);
    const context = await createContext(browser);
    const page = await context.newPage();
    
    const status = await checkLoginStatus(page);
    
    if (status.loggedIn) {
      console.log('已登录');
      console.log(`用户名: ${status.userName}`);
      process.exit(0);
    } else {
      console.log('未登录');
      console.log('请先运行 login skill 进行登录');
      console.log('\n登录命令:');
      console.log('  node ../login/scripts/login.js');
      process.exit(1);
    }
  } catch (error) {
    console.error('检查失败:', error.message);
    process.exit(1);
  } finally {
    if (browser) await browser.close();
  }
}

main();
