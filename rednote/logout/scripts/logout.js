#!/usr/bin/env node

const path = require('path');

const libPath = path.join(__dirname, '..', 'lib');
const { closeAll } = require(path.join(libPath, 'browser'));
const { CookieManager } = require(path.join(libPath, 'cookie'));
const { logger } = require(path.join(libPath, 'utils'));

const DATA_PATH = process.env.XHS_DATA_PATH || path.join(__dirname, '..', '..', 'data');

async function logout(options = {}) {
  const dataPath = options.dataPath || DATA_PATH;
  
  logger.info('执行登出操作...');
  logger.info(`数据路径: ${dataPath}`);
  
  try {
    logger.info('关闭浏览器实例...');
    await closeAll();
    
    const cookieManager = new CookieManager(dataPath);
    
    logger.info('清除 Cookie 和登录数据...');
    const clearResult = await cookieManager.clear();
    
    if (clearResult.success) {
      logger.info('登出成功');
      
      return {
        success: true,
        message: '已清除所有登录数据',
      };
    } else {
      logger.warn('部分数据清除失败:', clearResult.error);
      
      return {
        success: true,
        message: '已清除部分登录数据',
        warning: clearResult.error,
      };
    }
    
  } catch (error) {
    logger.error('登出失败:', error.message);
    
    return {
      success: false,
      error: error.message,
      message: '登出失败',
    };
  }
}

async function main() {
  const result = await logout();
  
  console.log('\n' + '='.repeat(50));
  
  if (result.success) {
    console.log('✅', result.message);
    
    if (result.warning) {
      console.log('⚠️ 警告:', result.warning);
    }
    
    console.log('\n请执行 get-qrcode 重新登录');
  } else {
    console.log('❌', result.message);
    console.log('错误:', result.error);
  }
  
  console.log('='.repeat(50) + '\n');
  
  process.exit(result.success ? 0 : 1);
}

if (require.main === module) {
  main();
}

module.exports = { logout };
