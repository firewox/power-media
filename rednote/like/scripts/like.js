#!/usr/bin/env node

const path = require('path');

const libPath = path.join(__dirname, '..', '..', 'lib');
const { getBrowserManager, closeAll } = require(path.join(libPath, 'browser'));
const { logger, randomSleep } = require(path.join(libPath, 'utils'));

const DATA_PATH = process.env.XHS_DATA_PATH || path.join(__dirname, '..', '..', 'data');
const EXPLORE_URL = 'https://www.xiaohongshu.com/explore/';

async function like(params) {
  const { noteId, unlike = false } = params;
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
  
  logger.info(`${unlike ? '取消点赞' : '点赞'}笔记: ${targetNoteId}`);
  
  const browserManager = getBrowserManager(dataPath, { headless: false });
  
  try {
    const page = await browserManager.getPage();
    
    const url = `${EXPLORE_URL}${targetNoteId}`;
    logger.info(`访问笔记页面: ${url}`);
    
    await page.goto(url, { waitUntil: 'domcontentloaded' });
    await randomSleep(2000, 3000);
    
    const likeSelectors = [
      '.like-wrapper, [class*="like-btn"]',
      '[class*="interact"] [class*="like"]',
      'button[class*="like"]',
      '.engagement-bar .like',
    ];
    
    let likeBtn = null;
    for (const selector of likeSelectors) {
      likeBtn = await page.$(selector);
      if (likeBtn) break;
    }
    
    if (!likeBtn) {
      throw new Error('未找到点赞按钮');
    }
    
    await likeBtn.click();
    logger.info('已点击点赞按钮');
    
    await randomSleep(1000, 2000);
    
    return {
      success: true,
      liked: !unlike,
      message: unlike ? '取消点赞成功' : '点赞成功',
    };
    
  } catch (error) {
    logger.error('点赞操作失败:', error.message);
    
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
    } else if (args[i] === '--unlike') {
      params.unlike = true;
    }
  }
  
  if (!params.noteId) {
    console.log('Usage: node like.js --noteId "笔记ID" [--unlike]');
    process.exit(1);
  }
  
  const result = await like(params);
  
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

module.exports = { like };
