#!/usr/bin/env node

const path = require('path');

const libPath = path.join(__dirname, '..', '..', 'lib');
const { getBrowserManager, closeAll } = require(path.join(libPath, 'browser'));
const { logger, randomSleep } = require(path.join(libPath, 'utils'));

const DATA_PATH = process.env.XHS_DATA_PATH || path.join(__dirname, '..', '..', 'data');
const EXPLORE_URL = 'https://www.xiaohongshu.com/explore/';

async function comment(params) {
  const { noteId, content } = params;
  const dataPath = params.dataPath || DATA_PATH;
  
  let targetNoteId = noteId;
  
  if (!targetNoteId) {
    throw new Error('笔记 ID 不能为空');
  }
  
  if (!content) {
    throw new Error('评论内容不能为空');
  }
  
  if (targetNoteId.includes('xiaohongshu.com')) {
    const match = targetNoteId.match(/\/explore\/(\w+)/);
    if (match) {
      targetNoteId = match[1];
    }
  }
  
  logger.info(`发表评论: ${targetNoteId}`);
  logger.info(`评论内容: ${content}`);
  
  const browserManager = getBrowserManager(dataPath, { headless: false });
  
  try {
    const page = await browserManager.getPage();
    
    const url = `${EXPLORE_URL}${targetNoteId}`;
    logger.info(`访问笔记页面: ${url}`);
    
    await page.goto(url, { waitUntil: 'domcontentloaded' });
    await randomSleep(2000, 3000);
    
    const inputSelectors = [
      'textarea[placeholder*="说点什么"]',
      '.comment-input textarea',
      '[class*="comment"] textarea',
      '[class*="comment-input"]',
    ];
    
    let commentInput = null;
    for (const selector of inputSelectors) {
      commentInput = await page.$(selector);
      if (commentInput) break;
    }
    
    if (!commentInput) {
      const commentBtn = await page.$('[class*="comment-btn"], button:has-text("评论")');
      if (commentBtn) {
        await commentBtn.click();
        await randomSleep(1000, 2000);
        
        for (const selector of inputSelectors) {
          commentInput = await page.$(selector);
          if (commentInput) break;
        }
      }
    }
    
    if (!commentInput) {
      throw new Error('未找到评论输入框');
    }
    
    await commentInput.click();
    await randomSleep(500, 1000);
    
    await page.keyboard.type(content, { delay: 50 });
    logger.info('已填写评论内容');
    
    await randomSleep(500, 1000);
    
    const submitSelectors = [
      'button:has-text("发送")',
      'button:has-text("提交")',
      '[class*="submit"]',
      '[class*="send-btn"]',
    ];
    
    let submitBtn = null;
    for (const selector of submitSelectors) {
      submitBtn = await page.$(selector);
      if (submitBtn) break;
    }
    
    if (!submitBtn) {
      await page.keyboard.press('Enter');
      logger.info('按 Enter 提交评论');
    } else {
      await submitBtn.click();
      logger.info('点击提交评论');
    }
    
    await randomSleep(2000, 3000);
    
    return {
      success: true,
      message: '评论发表成功',
    };
    
  } catch (error) {
    logger.error('评论发表失败:', error.message);
    
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
    } else if (args[i] === '--content' && args[i + 1]) {
      params.content = args[i + 1];
      i++;
    }
  }
  
  if (!params.noteId || !params.content) {
    console.log('Usage: node comment.js --noteId "笔记ID" --content "评论内容"');
    process.exit(1);
  }
  
  const result = await comment(params);
  
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

module.exports = { comment };
