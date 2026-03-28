#!/usr/bin/env node

const fs = require('fs');
const { launchBrowser, createContext, checkLoginStatus, postWithImage } = require('../../lib/weibo.js');

function showUsage() {
  console.log('用法: node post-with-image.js "微博内容" "/path/to/image.jpg"');
  console.log('');
  console.log('示例:');
  console.log('  node post-with-image.js "分享美景" "./photo.jpg"');
  process.exit(1);
}

async function main() {
  const text = process.argv[2];
  const imagePath = process.argv[3];
  
  if (!text || !imagePath) {
    showUsage();
  }
  
  if (text.length > 140) {
    console.error('错误: 微博内容不能超过 140 个字符');
    console.error(`当前长度: ${text.length} 字符`);
    process.exit(1);
  }
  
  if (!fs.existsSync(imagePath)) {
    console.error(`错误: 图片文件不存在: ${imagePath}`);
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
    console.log('正在发布带图片的微博...');
    console.log(`图片: ${imagePath}`);
    
    const result = await postWithImage(page, text, imagePath);
    
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
