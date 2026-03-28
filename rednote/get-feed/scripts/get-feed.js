#!/usr/bin/env node

const path = require('path');

const libPath = path.join(__dirname, '..', '..', 'lib');
const { getBrowserManager, closeAll } = require(path.join(libPath, 'browser'));
const { logger, randomSleep } = require(path.join(libPath, 'utils'));

const DATA_PATH = process.env.XHS_DATA_PATH || path.join(__dirname, '..', '..', 'data');
const EXPLORE_URL = 'https://www.xiaohongshu.com/explore/';

async function getFeed(params) {
  const { noteId, loadComments = false } = params;
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
  
  logger.info(`获取帖子详情: ${targetNoteId}`);
  
  const browserManager = getBrowserManager(dataPath, { headless: false });
  
  try {
    const page = await browserManager.getPage();
    
    const url = `${EXPLORE_URL}${targetNoteId}`;
    logger.info(`访问帖子页面: ${url}`);
    
    await page.goto(url, { waitUntil: 'domcontentloaded' });
    await randomSleep(3000, 5000);
    
    const feed = await page.evaluate(() => {
      const state = window.__INITIAL_STATE__;
      
      if (state?.note?.noteDetail) {
        const noteData = state.note.noteDetail;
        const note = noteData.note || noteData;
        
        return {
          noteId: note.noteId,
          title: note.title || '',
          content: note.desc || '',
          type: note.type || 'normal',
          author: {
            userId: note.user?.userId || '',
            username: note.user?.nickname || '',
            avatar: note.user?.image || '',
          },
          images: (note.imageList || []).map(img => img.urlDefault || img),
          video: note.video?.media?.stream?.h264?.[0]?.masterUrl || null,
          interactInfo: {
            likes: note.interactInfo?.likedCount || 0,
            collects: note.interactInfo?.collectedCount || 0,
            comments: note.interactInfo?.commentCount || 0,
            shares: note.interactInfo?.shareCount || 0,
          },
          tags: (note.tagList || []).map(tag => tag.name || tag),
          time: note.time || '',
          url: `https://www.xiaohongshu.com/explore/${note.noteId}`,
        };
      }
      
      const titleEl = document.querySelector('.title, [class*="title"]');
      const contentEl = document.querySelector('.content, [class*="desc"], .note-text');
      const authorEl = document.querySelector('.author-name, [class*="author"] .name, .user-name');
      const imagesEl = document.querySelectorAll('.swiper-slide img, [class*="image"] img');
      
      return {
        noteId: window.location.pathname.split('/').pop(),
        title: titleEl?.textContent?.trim() || '',
        content: contentEl?.textContent?.trim() || '',
        author: {
          username: authorEl?.textContent?.trim() || '',
        },
        images: Array.from(imagesEl).map(img => img.src || img.dataset.src).filter(Boolean),
        url: window.location.href,
      };
    });
    
    if (loadComments) {
      logger.info('加载评论...');
      await randomSleep(2000, 3000);
      
      const comments = await page.evaluate(() => {
        const state = window.__INITIAL_STATE__;
        if (state?.note?.noteDetail?.comments) {
          return state.note.noteDetail.comments.map(c => ({
            id: c.id,
            content: c.content,
            author: c.user?.nickname || '',
            likes: c.likeCount || 0,
            time: c.time || '',
          }));
        }
        
        const commentEls = document.querySelectorAll('.comment-item, [class*="comment"]');
        return Array.from(commentEls).slice(0, 20).map(el => ({
          content: el.querySelector('.content, [class*="content"]')?.textContent?.trim() || '',
          author: el.querySelector('.name, [class*="name"]')?.textContent?.trim() || '',
        }));
      });
      
      feed.comments = comments;
    }
    
    logger.info('帖子详情获取成功');
    
    return {
      success: true,
      feed,
    };
    
  } catch (error) {
    logger.error('获取帖子详情失败:', error.message);
    
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
    } else if (args[i] === '--comments') {
      params.loadComments = true;
    }
  }
  
  if (!params.noteId) {
    console.log('Usage: node get-feed.js --noteId "笔记ID或URL" [--comments]');
    process.exit(1);
  }
  
  const result = await getFeed(params);
  
  console.log('\n' + '='.repeat(50));
  
  if (result.success) {
    console.log('标题:', result.feed.title);
    console.log('作者:', result.feed.author?.username);
    console.log('点赞:', result.feed.interactInfo?.likes || 0);
    console.log('收藏:', result.feed.interactInfo?.collects || 0);
    console.log('评论:', result.feed.interactInfo?.comments || 0);
    console.log('\n内容:\n', result.feed.content?.slice(0, 200));
    
    if (result.feed.comments) {
      console.log('\n评论:', result.feed.comments.length, '条');
    }
  } else {
    console.log('获取失败:', result.error);
  }
  
  console.log('='.repeat(50));
  
  process.exit(result.success ? 0 : 1);
}

if (require.main === module) {
  main();
}

module.exports = { getFeed };
