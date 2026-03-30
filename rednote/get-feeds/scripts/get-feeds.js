#!/usr/bin/env node

const path = require('path');

const libPath = path.join(__dirname, '..', '..', 'lib');
const { SystemBrowserManager } = require(path.join(libPath, 'system-browser'));
const { logger, randomSleep } = require(path.join(libPath, 'utils'));

const DATA_PATH = process.env.XHS_DATA_PATH || path.join(__dirname, '..', '..', 'data');
const HOME_URL = 'https://www.xiaohongshu.com/';

async function getFeeds(params = {}) {
  const { count = 20 } = params;
  const dataPath = params.dataPath || DATA_PATH;
  
  logger.info('获取推荐列表...');
  
  const browserManager = new SystemBrowserManager({ headless: false });
  
  try {
    const page = await browserManager.getPage();
    
    logger.info(`访问首页: ${HOME_URL}`);
    await page.goto(HOME_URL, { waitUntil: 'domcontentloaded' });
    await randomSleep(3000, 5000);
    
    const feeds = await page.evaluate(() => {
      const results = [];
      
      const state = window.__INITIAL_STATE__;
      if (state?.home?.feeds) {
        const feedData = state.home.feeds.value || state.home.feeds;
        if (Array.isArray(feedData)) {
          for (const feed of feedData) {
            const noteCard = feed.noteCard || feed;
            results.push({
              noteId: noteCard.noteId || feed.id,
              title: noteCard.displayTitle || noteCard.title || '',
              author: noteCard.user?.nickname || '',
              authorId: noteCard.user?.userId || '',
              likes: noteCard.interactInfo?.likedCount || 0,
              cover: noteCard.cover?.url || noteCard.cover?.urlDefault || '',
              type: noteCard.type || 'normal',
              url: `https://www.xiaohongshu.com/explore/${noteCard.noteId || feed.id}`,
            });
          }
        }
      }
      
      if (results.length === 0) {
        const items = document.querySelectorAll('.note-item, [class*="feed-item"], [class*="note-card"]');
        items.forEach(item => {
          const link = item.querySelector('a');
          const titleEl = item.querySelector('.title, [class*="title"]');
          const authorEl = item.querySelector('.author, [class*="author"], .name');
          const imgEl = item.querySelector('img');
          
          if (link) {
            const href = link.getAttribute('href') || '';
            const noteIdMatch = href.match(/\/explore\/(\w+)/);
            
            results.push({
              noteId: noteIdMatch ? noteIdMatch[1] : '',
              title: titleEl?.textContent?.trim() || '',
              author: authorEl?.textContent?.trim() || '',
              cover: imgEl?.src || '',
              url: href.startsWith('http') ? href : `https://www.xiaohongshu.com${href}`,
            });
          }
        });
      }
      
      return results;
    });
    
    const result = feeds.slice(0, count);
    logger.info(`获取到 ${result.length} 条推荐`);
    
    return {
      success: true,
      feeds: result,
    };
    
  } catch (error) {
    logger.error('获取推荐列表失败:', error.message);
    
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
    if (args[i] === '--count' && args[i + 1]) {
      params.count = parseInt(args[i + 1], 10);
      i++;
    }
  }
  
  const result = await getFeeds(params);
  
  console.log('\n' + '='.repeat(50));
  
  if (result.success) {
    console.log(`推荐内容 (${result.feeds.length} 条):\n`);
    
    result.feeds.forEach((feed, i) => {
      console.log(`${i + 1}. ${feed.title || '(无标题)'}`);
      console.log(`   作者: ${feed.author || '未知'}`);
      console.log(`   点赞: ${feed.likes || 0}`);
    });
  } else {
    console.log('获取失败:', result.error);
  }
  
  console.log('='.repeat(50));
  
  process.exit(result.success ? 0 : 1);
}

if (require.main === module) {
  main();
}

module.exports = { getFeeds };
