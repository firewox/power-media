#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const COOKIE_FILE = path.join(__dirname, '..', '..', '.cookies.json');

async function main() {
  console.log('正在退出微博...\n');
  
  try {
    if (fs.existsSync(COOKIE_FILE)) {
      fs.unlinkSync(COOKIE_FILE);
      console.log('Cookie 已清除');
      console.log('退出成功');
      process.exit(0);
    } else {
      console.log('未找到 Cookie 文件');
      console.log('已经处于未登录状态');
      process.exit(0);
    }
  } catch (error) {
    console.error('退出失败:', error.message);
    process.exit(1);
  }
}

main();
