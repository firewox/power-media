#!/usr/bin/env node

const path = require('path');

const libPath = path.join(__dirname, '..', 'lib');
const { getBrowserManager, closeAll } = require(path.join(libPath, 'browser'));
const { logger, randomSleep } = require(path.join(libPath, 'utils'));

const DATA_PATH = process.env.XHS_DATA_PATH || path.join(__dirname, '..', '..', 'data');
const PROFILE_URL = 'https://www.xiaohongshu.com/user/profile/';

async function getProfile(params) {
  const { userId } = params;
  const dataPath = params.dataPath || DATA_PATH;
  
  let targetUserId = userId;
  
  if (!targetUserId) {
    throw new Error('用户 ID 不能为空');
  }
  
  if (targetUserId.includes('xiaohongshu.com')) {
    const match = targetUserId.match(/\/user\/profile\/(\w+)/);
    if (match) {
      targetUserId = match[1];
    }
  }
  
  logger.info(`获取用户主页: ${targetUserId}`);
  
  const browserManager = getBrowserManager(dataPath, { headless: false });
  
  try {
    const page = await browserManager.getPage();
    
    const url = `${PROFILE_URL}${targetUserId}`;
    logger.info(`访问用户主页: ${url}`);
    
    await page.goto(url, { waitUntil: 'domcontentloaded' });
    await randomSleep(3000, 5000);
    
    const profile = await page.evaluate(() => {
      const state = window.__INITIAL_STATE__;
      
      if (state?.user?.userPage) {
        const userData = state.user.userPage;
        const user = userData.user || userData;
        const notes = userData.notes || [];
        
        return {
          userId: user.userId || user.id,
          username: user.nickname || user.name || '',
          avatar: user.image || user.avatar || '',
          desc: user.desc || user.signature || '',
          location: user.location || '',
          fans: user.fansCount || user.fans || 0,
          follows: user.followsCount || user.following || 0,
          liked: user.likedCount || user.liked || 0,
          notes: notes.slice(0, 20).map(note => ({
            noteId: note.noteId || note.id,
            title: note.displayTitle || note.title || '',
            cover: note.cover?.url || note.cover || '',
            likes: note.interactInfo?.likedCount || note.likes || 0,
            url: `https://www.xiaohongshu.com/explore/${note.noteId || note.id}`,
          })),
          url: `https://www.xiaohongshu.com/user/profile/${user.userId || user.id}`,
        };
      }
      
      const usernameEl = document.querySelector('.user-name, [class*="user-name"], .name');
      const descEl = document.querySelector('.user-desc, [class*="desc"], .signature');
      const avatarEl = document.querySelector('.user-avatar img, [class*="avatar"] img');
      const fansEl = document.querySelector('.fans-count, [class*="fans"]');
      const followsEl = document.querySelector('.follows-count, [class*="follow"]');
      
      const noteItems = document.querySelectorAll('.note-item, [class*="note"]');
      const notes = Array.from(noteItems).slice(0, 20).map(item => {
        const link = item.querySelector('a');
        const titleEl = item.querySelector('.title, [class*="title"]');
        const imgEl = item.querySelector('img');
        
        const href = link?.getAttribute('href') || '';
        const noteIdMatch = href.match(/\/explore\/(\w+)/);
        
        return {
          noteId: noteIdMatch ? noteIdMatch[1] : '',
          title: titleEl?.textContent?.trim() || '',
          cover: imgEl?.src || '',
          url: href.startsWith('http') ? href : `https://www.xiaohongshu.com${href}`,
        };
      });
      
      return {
        userId: window.location.pathname.split('/').pop(),
        username: usernameEl?.textContent?.trim() || '',
        desc: descEl?.textContent?.trim() || '',
        avatar: avatarEl?.src || '',
        fans: fansEl?.textContent?.trim() || '0',
        follows: followsEl?.textContent?.trim() || '0',
        notes,
        url: window.location.href,
      };
    });
    
    logger.info('用户主页获取成功');
    
    return {
      success: true,
      profile,
    };
    
  } catch (error) {
    logger.error('获取用户主页失败:', error.message);
    
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
    if (args[i] === '--userId' && args[i + 1]) {
      params.userId = args[i + 1];
      i++;
    }
  }
  
  if (!params.userId) {
    console.log('Usage: node get-profile.js --userId "用户ID或URL"');
    process.exit(1);
  }
  
  const result = await getProfile(params);
  
  console.log('\n' + '='.repeat(50));
  
  if (result.success) {
    console.log('用户名:', result.profile.username);
    console.log('简介:', result.profile.desc);
    console.log('粉丝:', result.profile.fans);
    console.log('关注:', result.profile.follows);
    console.log('笔记数:', result.profile.notes?.length || 0);
    
    if (result.profile.notes?.length > 0) {
      console.log('\n最近笔记:');
      result.profile.notes.slice(0, 5).forEach((note, i) => {
        console.log(`  ${i + 1}. ${note.title || '(无标题)'}`);
      });
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

module.exports = { getProfile };
