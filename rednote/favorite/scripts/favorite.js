#!/usr/bin/env node

const path = require('path');

const libPath = path.join(__dirname, '..', '..', 'lib');
const { getBrowserManager, closeAll } = require(path.join(libPath, 'browser'));
const { logger, randomSleep } = require(path.join(libPath, 'utils'));

const DATA_PATH = process.env.XHS_DATA_PATH || path.join(__dirname, '..', '..', 'data');
const EXPLORE_URL = 'https://www.xiaohongshu.com/explore/';

async function favorite(params) {
  const { noteId, unfavorite = false } = params;
  const dataPath = params.dataPath || DATA_PATH;
  
  let targetNoteId = noteId;
  
  if (!targetNoteId) {
    throw new Error('笔记 ID 不能为空');
  }
  
  if (targetNoteId.includes('xiaohongshu.com')) {
    const match = targetNoteId.match(/\/explore\/(\w+)/);
    if (match) {
      targetNoteId = match[1];
    }
  }
  
  logger.info(`${unfavorite ? '取消收藏' : '收藏'}笔记: ${targetNoteId}`);
  
  const browserManager = getBrowserManager(dataPath, { headless: false });
  
  try {
    const page = await browserManager.getPage();
    
    const url = `${EXPLORE_URL}${targetNoteId}`;
    logger.info(`访问笔记页面: ${url}`);
    
    await page.goto(url, { waitUntil: 'domcontentloaded' });
    await randomSleep(2000, 3000);
    
    const favoriteSelectors = [
      '.collect-wrapper, [class*="collect-btn"]',
      '[class*="interact"] [class*="collect"]',
      'button[class*="collect"]',
      '.engagement-bar .collect',
      '[class*="favorite"]',
    ];
    
    let favoriteBtn = null;
    for (const selector of favoriteSelectors) {
      favoriteBtn = await page.$(selector);
      if (favoriteBtn) break;
    }
    
    if (!favoriteBtn) {
      throw new Error('未找到收藏按钮');
    }
    
    await favoriteBtn.click();
    logger.info('已点击收藏按钮');
    
    await randomSleep(1000, 2000);
    
    return {
      success: true,
      favorited: !unfavorite,
      message: unfavorite ? '取消收藏成功' : '收藏成功',
    };
    
  } catch (error) {
    logger.error('收藏操作失败:', error.message);
    
    return {
      success: false,
      error: error.message,
    };
  }
}

async function main() {
  const args = process.argv.slice(2);
  
  const params = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--noteId' && args[i + 1]) {
      params.noteId = args[i + 1];
      i++;
    } else if (args[i] === '--unfavorite') {
      params.unfavorite = true;
    }
  }
  
  if (!params.noteId) {
    console.log('Usage: node favorite.js --noteId "笔记ID" [--unfavorite]');
    process.exit(1);
  }
  
  const result = await favorite(params);
  
  console.log('\n' + '='.repeat(50));
  
  if (result.success) {
    console.log('✅', result.message);
  } else {
    console.log('❌ 操作失败:', result.error);
  }
  
  console.log('='.repeat(50));
  
  process.exit(result.success ? 0 : 1);
}

if (require.main === module) {
  main();
}

module.exports = { favorite };
