#!/usr/bin/env node

const { launchBrowser, createContext, checkLoginStatus, postText } = require('../../lib/weibo.js');

function showUsage() {
  console.log('用法: node post-text.js "微博内容"');
  console.log('');
  console.log('示例:');
  console.log('  node post-text.js "Hello Weibo!"');
  process.exit(1);
}

async function main() {
  const text = process.argv[2];
  
  if (!text) {
    showUsage();
  }
  
  if (text.length > 140) {
    console.error('错误: 微博内容不能超过 140 个字符');
    console.error(`当前长度: ${text.length} 字符`);
    process.exit(1);
  }
  
  console.log('正在检查登录状态...');
  
  let browser;
  try {
    browser = await launchBrowser(true);
    const context = await createContext(browser);
    const page = await context.newPage();
    
    const loginStatus = await checkLoginStatus(page);
    
    if (!loginStatus.loggedIn) {
      console.log('未登录');
      console.log('请先运行 login skill 进行登录');
      console.log('');
      console.log('登录命令:');
      console.log('  node ../login/scripts/login.js');
      process.exit(1);
    }
    
    console.log(`已登录: ${loginStatus.userName}\n`);
    console.log('正在发布微博...');
    
    const result = await postText(page, text);
    
    if (result.success) {
      console.log('发布成功！');
      if (result.message) {
        console.log(result.message);
      }
      process.exit(0);
    } else {
      console.error('发布失败:', result.error || '未知错误');
      process.exit(1);
    }
  } catch (error) {
    console.error('发布失败:', error.message);
    process.exit(1);
  } finally {
    if (browser) await browser.close();
  }
}

main();
