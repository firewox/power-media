#!/usr/bin/env node

const path = require('path');

const libPath = path.join(__dirname, '..', 'lib');
const { getBrowserManager, closeAll } = require(path.join(libPath, 'browser'));
const { logger, randomSleep } = require(path.join(libPath, 'utils'));

const DATA_PATH = process.env.XHS_DATA_PATH || path.join(__dirname, '..', '..', 'data');
const EXPLORE_URL = 'https://www.xiaohongshu.com/explore/';

async function reply(params) {
  const { noteId, commentId, content } = params;
  const dataPath = params.dataPath || DATA_PATH;
  
  let targetNoteId = noteId;
  
  if (!targetNoteId) {
    throw new Error('笔记 ID 不能为空');
  }
  
  if (!content) {
    throw new Error('回复内容不能为空');
  }
  
  if (targetNoteId.includes('xiaohongshu.com')) {
    const match = targetNoteId.match(/\/explore\/(\w+)/);
    if (match) {
      targetNoteId = match[1];
    }
  }
  
  logger.info(`回复评论: ${targetNoteId}`);
  logger.info(`回复内容: ${content}`);
  
  const browserManager = getBrowserManager(dataPath, { headless: false });
  
  try {
    const page = await browserManager.getPage();
    
    const url = `${EXPLORE_URL}${targetNoteId}`;
    logger.info(`访问笔记页面: ${url}`);
    
    await page.goto(url, { waitUntil: 'domcontentloaded' });
    await randomSleep(2000, 3000);
    
    if (commentId) {
      const commentEl = await page.$(`[data-comment-id="${commentId}"], [data-id="${commentId}"]`);
      if (commentEl) {
        const replyBtn = await commentEl.$('[class*="reply"], button:has-text("回复")');
        if (replyBtn) {
          await replyBtn.click();
          await randomSleep(500, 1000);
        }
      }
    }
    
    const inputSelectors = [
      'textarea[placeholder*="说点什么"]',
      '.comment-input textarea',
      '[class*="comment"] textarea',
      '[class*="reply-input"]',
    ];
    
    let inputEl = null;
    for (const selector of inputSelectors) {
      inputEl = await page.$(selector);
      if (inputEl) break;
    }
    
    if (!inputEl) {
      const replyBtns = await page.$$('button:has-text("回复"), [class*="reply-btn"]');
      if (replyBtns.length > 0) {
        await replyBtns[0].click();
        await randomSleep(500, 1000);
        
        for (const selector of inputSelectors) {
          inputEl = await page.$(selector);
          if (inputEl) break;
        }
      }
    }
    
    if (!inputEl) {
      throw new Error('未找到回复输入框');
    }
    
    await inputEl.click();
    await randomSleep(500, 1000);
    
    await page.keyboard.type(content, { delay: 50 });
    logger.info('已填写回复内容');
    
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
      logger.info('按 Enter 提交回复');
    } else {
      await submitBtn.click();
      logger.info('点击提交回复');
    }
    
    await randomSleep(2000, 3000);
    
    return {
      success: true,
      message: '回复发表成功',
    };
    
  } catch (error) {
    logger.error('回复发表失败:', error.message);
    
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
    } else if (args[i] === '--commentId' && args[i + 1]) {
      params.commentId = args[i + 1];
      i++;
    } else if (args[i] === '--content' && args[i + 1]) {
      params.content = args[i + 1];
      i++;
    }
  }
  
  if (!params.noteId || !params.content) {
    console.log('Usage: node reply.js --noteId "笔记ID" [--commentId "评论ID"] --content "回复内容"');
    process.exit(1);
  }
  
  const result = await reply(params);
  
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

module.exports = { reply };
