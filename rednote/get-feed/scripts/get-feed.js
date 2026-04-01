#!/usr/bin/env node

const path = require('path');

const libPath = path.join(__dirname, '..', '..', 'lib');
const { SystemBrowserManager } = require(path.join(libPath, 'system-browser'));
const { logger, randomSleep } = require(path.join(libPath, 'utils'));

const DATA_PATH = process.env.XHS_DATA_PATH || path.join(__dirname, '..', '..', 'data');
const SEARCH_URL = 'https://www.xiaohongshu.com/search_result';
const HOME_URL = 'https://www.xiaohongshu.com/';

async function getFeed(params) {
  const { noteId, loadComments = false, keyword } = params;
  
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
    
    let found = false;
    
    // 策略1: 如果提供了关键词，通过搜索点击笔记
    if (keyword) {
      logger.info(`通过关键词"${keyword}"搜索...`);
      const searchUrl = `${SEARCH_URL}?keyword=${encodeURIComponent(keyword)}`;
      await page.goto(searchUrl, { waitUntil: 'networkidle' });
      await randomSleep(3000, 5000);
      
      // 尝试点击笔记卡片
      const selectors = ['.note-item', '[class*="note-item"]', '[class*="feeds-item"]'];
      
      for (const selector of selectors) {
        try {
          const count = await page.locator(selector).count();
          if (count > 0) {
            // 检查是否有目标笔记
            const foundIndex = await page.evaluate(({ sel, targetId }) => {
              const items = document.querySelectorAll(sel);
              for (let i = 0; i < items.length; i++) {
                const link = items[i].querySelector(`a[href*="/explore/${targetId}"]`);
                if (link) return i;
              }
              return -1;
            }, { sel: selector, targetId: targetNoteId });
            
            if (foundIndex >= 0) {
              await page.locator(selector).nth(foundIndex).click({ force: true });
              logger.info(`点击笔记卡片成功 (位置 ${foundIndex})`);
              found = true;
              break;
            } else {
              // 点击第一个笔记
              await page.locator(selector).first().click({ force: true });
              logger.info('点击第一个笔记卡片');
              found = true;
              break;
            }
          }
        } catch (e) {
          logger.debug(`选择器 ${selector} 点击失败: ${e.message}`);
        }
      }
    }
    
    // 策略2: 如果没有关键词或搜索失败，尝试从首页推荐点击
    if (!found && !keyword) {
      logger.info('尝试从首页推荐点击...');
      await page.goto(HOME_URL, { waitUntil: 'networkidle' });
      await randomSleep(3000, 5000);
      
      const selectors = ['.note-item', '[class*="note-item"]', '[class*="feeds-item"]'];
      
      for (const selector of selectors) {
        try {
          const count = await page.locator(selector).count();
          if (count > 0) {
            await page.locator(selector).first().click({ force: true });
            logger.info('点击首页推荐笔记');
            found = true;
            break;
          }
        } catch (e) {
          logger.debug(`选择器 ${selector} 点击失败`);
        }
      }
    }
    
    // 策略3: 直接访问（可能失败）
    if (!found) {
      logger.warn('点击失败，尝试直接访问...');
      await page.goto(`https://www.xiaohongshu.com/explore/${targetNoteId}`, { waitUntil: 'networkidle' });
      await randomSleep(3000, 5000);
    }
    
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
          url: window.location.href,
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
          url: window.location.href,
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
    console.log('  --keyword  搜索关键词（通过点击笔记卡片获取详情）');
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
