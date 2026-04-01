#!/usr/bin/env node

const path = require('path');

const libPath = path.join(__dirname, '..', '..', 'lib');
const { SystemBrowserManager } = require(path.join(libPath, 'system-browser'));
const { logger, randomSleep } = require(path.join(libPath, 'utils'));

const DATA_PATH = process.env.XHS_DATA_PATH || path.join(__dirname, '..', '..', 'data');
const SEARCH_URL = 'https://www.xiaohongshu.com/search_result';
const EXPLORE_URL = 'https://www.xiaohongshu.com/explore/';

async function getFeed(params) {
  const { noteId, loadComments = false, keyword } = params;
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
  
  const browserManager = new SystemBrowserManager({ headless: false });
  
  try {
    const page = await browserManager.getPage();
    
    let xsecToken = null;
    let xsecSource = 'pc_feed';
    
    // 策略1: 如果提供了关键词，通过搜索获取 xsecToken
    if (keyword) {
      logger.info(`通过关键词"${keyword}"搜索获取 xsecToken...`);
      const searchUrl = `${SEARCH_URL}?keyword=${encodeURIComponent(keyword)}`;
      await page.goto(searchUrl, { waitUntil: 'networkidle' });
      await randomSleep(3000, 5000);
      
      const searchResult = await page.evaluate((targetId) => {
        const state = window.__INITIAL_STATE__;
        const feeds = state?.search?.feeds?.value || [];
        
        for (const feed of feeds) {
          const feedNoteId = feed.noteCard?.noteId || feed.id;
          if (feedNoteId === targetId) {
            return {
              found: true,
              xsecToken: feed.xsecToken,
              displayTitle: feed.noteCard?.displayTitle
            };
          }
        }
        return { found: false };
      }, targetNoteId);
      
      if (searchResult.found) {
        xsecToken = searchResult.xsecToken;
        xsecSource = 'pc_search';
        logger.info(`从搜索结果获取到 xsecToken`);
      }
    }
    
    // 策略2: 如果没有关键词或搜索没找到，尝试从首页推荐获取
    if (!xsecToken) {
      logger.info('尝试从首页推荐获取 xsecToken...');
      await page.goto('https://www.xiaohongshu.com/', { waitUntil: 'networkidle' });
      await randomSleep(3000, 5000);
      
      const feedResult = await page.evaluate((targetId) => {
        const state = window.__INITIAL_STATE__;
        const feeds = state?.feed?.feeds?.value || [];
        
        for (const feed of feeds) {
          const feedNoteId = feed.noteCard?.noteId || feed.id;
          if (feedNoteId === targetId) {
            return {
              found: true,
              xsecToken: feed.xsecToken
            };
          }
        }
        return { found: false };
      }, targetNoteId);
      
      if (feedResult.found) {
        xsecToken = feedResult.xsecToken;
        xsecSource = 'pc_feed';
        logger.info(`从首页推荐获取到 xsecToken`);
      }
    }
    
    // 构建访问 URL
    let noteUrl;
    if (xsecToken) {
      noteUrl = `${EXPLORE_URL}${targetNoteId}?xsec_token=${encodeURIComponent(xsecToken)}&xsec_source=${xsecSource}`;
      logger.info('使用 xsecToken 访问笔记详情');
    } else {
      noteUrl = `${EXPLORE_URL}${targetNoteId}`;
      logger.warn('未获取到 xsecToken，直接访问可能失败');
    }
    
    logger.info(`访问: ${noteUrl}`);
    await page.goto(noteUrl, { waitUntil: 'networkidle' });
    await randomSleep(3000, 5000);
    
    // 提取笔记数据
    const feed = await page.evaluate((noteId) => {
      const state = window.__INITIAL_STATE__;
      
      // 从 noteDetailMap 获取数据
      if (state?.note?.noteDetailMap?.[noteId]) {
        const noteData = state.note.noteDetailMap[noteId];
        const note = noteData.note || noteData;
        
        return {
          noteId: note.noteId || noteId,
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
          url: `https://www.xiaohongshu.com/explore/${note.noteId || noteId}`,
        };
      }
      
      // 从 noteDetail 获取数据（旧结构）
      if (state?.note?.noteDetail) {
        const noteData = state.note.noteDetail;
        const note = noteData.note || noteData;
        
        return {
          noteId: note.noteId || noteId,
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
          url: `https://www.xiaohongshu.com/explore/${note.noteId || noteId}`,
        };
      }
      
      // DOM 降级方案
      const titleEl = document.querySelector('.title, [class*="title"]');
      const contentEl = document.querySelector('.content, [class*="desc"], .note-text');
      const authorEl = document.querySelector('.author-name, [class*="author"] .name, .user-name');
      
      return {
        noteId: noteId,
        title: titleEl?.textContent?.trim() || '',
        content: contentEl?.textContent?.trim() || '',
        author: {
          username: authorEl?.textContent?.trim() || '',
        },
        url: window.location.href,
      };
    }, targetNoteId);
    
    // 加载评论
    if (loadComments) {
      logger.info('加载评论...');
      await randomSleep(2000, 3000);
      
      const comments = await page.evaluate((noteId) => {
        const state = window.__INITIAL_STATE__;
        const noteDetail = state?.note?.noteDetailMap?.[noteId];
        
        if (noteDetail?.comments) {
          return noteDetail.comments.map(c => ({
            id: c.id,
            content: c.content,
            author: c.user?.nickname || '',
            likes: c.likeCount || 0,
            time: c.time || '',
          }));
        }
        
        return [];
      }, targetNoteId);
      
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
    } else if (args[i] === '--keyword' && args[i + 1]) {
      params.keyword = args[i + 1];
      i++;
    } else if (args[i] === '--comments') {
      params.loadComments = true;
    }
  }
  
  if (!params.noteId) {
    console.log('Usage: node get-feed.js --noteId "笔记ID" [--keyword "搜索关键词"] [--comments]');
    console.log('\n说明:');
    console.log('  --noteId   笔记ID或完整URL');
    console.log('  --keyword  搜索关键词（用于获取 xsecToken，提高成功率）');
    console.log('  --comments 加载评论');
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
