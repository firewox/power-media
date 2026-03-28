#!/usr/bin/env node

const path = require('path');

const libPath = path.join(__dirname, '..', '..', 'lib');
const { getBrowserManager, closeAll } = require(path.join(libPath, 'browser'));
const { logger, randomSleep } = require(path.join(libPath, 'utils'));

const DATA_PATH = process.env.XHS_DATA_PATH || path.join(__dirname, '..', '..', 'data');
const SEARCH_URL = 'https://www.xiaohongshu.com/search_result';

async function search(params) {
  const { keyword, sortBy, noteType } = params;
  const dataPath = params.dataPath || DATA_PATH;
  
  if (!keyword) {
    throw new Error('搜索关键词不能为空');
  }
  
  logger.info(`搜索关键词: ${keyword}`);
  
  const browserManager = getBrowserManager(dataPath, { headless: false });
  
  try {
    const page = await browserManager.getPage();
    
    const searchUrl = `${SEARCH_URL}?keyword=${encodeURIComponent(keyword)}`;
    logger.info(`访问搜索页面: ${searchUrl}`);
    
    await page.goto(searchUrl, { waitUntil: 'domcontentloaded' });
    await randomSleep(3000, 5000);
    
    const feeds = await page.evaluate(() => {
      const results = [];
      
      const state = window.__INITIAL_STATE__;
      if (state?.search?.feeds) {
        const feedData = state.search.feeds.value || state.search.feeds;
        if (Array.isArray(feedData)) {
          for (const feed of feedData) {
            const noteCard = feed.noteCard || feed;
            results.push({
              noteId: noteCard.noteId || feed.id,
              title: noteCard.displayTitle || noteCard.title || '',
              author: noteCard.user?.nickname || '',
              likes: noteCard.interactInfo?.likedCount || 0,
              cover: noteCard.cover?.url || '',
              url: `https://www.xiaohongshu.com/explore/${noteCard.noteId || feed.id}`,
            });
          }
        }
      }
      
      if (results.length === 0) {
        const items = document.querySelectorAll('.note-item, [class*="note-card"]');
        items.forEach(item => {
          const link = item.querySelector('a');
          const titleEl = item.querySelector('.title, [class*="title"]');
          
          if (link) {
            const href = link.getAttribute('href') || '';
            const noteIdMatch = href.match(/\/explore\/(\w+)/);
            
            results.push({
              noteId: noteIdMatch ? noteIdMatch[1] : '',
              title: titleEl?.textContent?.trim() || '',
              url: href.startsWith('http') ? href : `https://www.xiaohongshu.com${href}`,
            });
          }
        });
      }
      
      return results;
    });
    
    logger.info(`找到 ${feeds.length} 条搜索结果`);
    
    return {
      success: true,
      keyword,
      feeds,
    };
    
  } catch (error) {
    logger.error('搜索失败:', error.message);
    
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
    if (args[i] === '--keyword' && args[i + 1]) {
      params.keyword = args[i + 1];
      i++;
    }
  }
  
  if (!params.keyword) {
    console.log('Usage: node search.js --keyword "搜索关键词"');
    process.exit(1);
  }
  
  const result = await search(params);
  
  console.log('\n' + '='.repeat(50));
  
  if (result.success) {
    console.log(`搜索关键词: ${result.keyword}`);
    console.log(`找到 ${result.feeds.length} 条结果\n`);
    
    result.feeds.slice(0, 10).forEach((feed, i) => {
      console.log(`${i + 1}. ${feed.title || '(无标题)'}`);
      console.log(`   作者: ${feed.author || '未知'}`);
      console.log(`   链接: ${feed.url}`);
    });
  } else {
    console.log('搜索失败:', result.error);
  }
  
  console.log('='.repeat(50));
  
  process.exit(result.success ? 0 : 1);
}

if (require.main === module) {
  main();
}

module.exports = { search };
