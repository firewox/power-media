#!/usr/bin/env node

const path = require('path');
const fs = require('fs');

const libPath = path.join(__dirname, '..', '..', 'lib');
const { getBrowserManager, closeAll } = require(path.join(libPath, 'browser'));
const { CookieManager } = require(path.join(libPath, 'cookie'));
const { logger, randomSleep } = require(path.join(libPath, 'utils'));

const DATA_PATH = process.env.XHS_DATA_PATH || path.join(__dirname, '..', '..', 'data');
const PUBLISH_URL = 'https://creator.xiaohongshu.com/publish/publish?source=official';

const LIMITS = {
  titleMax: 20,
  contentMax: 1000,
  tagMax: 10,
};

const VIDEO_MAX_SIZE = 1024 * 1024 * 1024; // 1GB

function validateInput(params) {
  const { title, content, video } = params;
  
  if (!title || title.length === 0) {
    throw new Error('标题不能为空');
  }
  if (title.length > LIMITS.titleMax) {
    throw new Error(`标题最多 ${LIMITS.titleMax} 个字`);
  }
  
  if (!content || content.length === 0) {
    throw new Error('内容不能为空');
  }
  if (content.length > LIMITS.contentMax) {
    throw new Error(`内容最多 ${LIMITS.contentMax} 个字`);
  }
  
  if (!video) {
    throw new Error('视频路径不能为空');
  }
  if (!fs.existsSync(video)) {
    throw new Error(`视频文件不存在: ${video}`);
  }
  
  const videoStats = fs.statSync(video);
  if (videoStats.size > VIDEO_MAX_SIZE) {
    throw new Error('视频文件大小超过 1GB 限制');
  }
  
  if (params.cover && !fs.existsSync(params.cover)) {
    throw new Error(`封面图片不存在: ${params.cover}`);
  }
  
  if (params.tags && params.tags.length > LIMITS.tagMax) {
    throw new Error(`最多添加 ${LIMITS.tagMax} 个话题标签`);
  }
  
  return true;
}

async function publishVideo(params) {
  const { title, content, video, cover, tags = [], visibility = 'public' } = params;
  const dataPath = params.dataPath || DATA_PATH;
  
  validateInput(params);
  
  logger.info('发布视频笔记...');
  logger.info(`标题: ${title}`);
  logger.info(`视频: ${video}`);
  logger.info(`封面: ${cover || '自动生成'}`);
  logger.info(`话题标签: ${tags.join(', ') || '无'}`);
  
  const browserManager = getBrowserManager(dataPath, { headless: false });
  const cookieManager = new CookieManager(dataPath);
  
  try {
    const page = await browserManager.getPage();
    
    const loginState = cookieManager.loadLoginState();
    if (!loginState?.isLoggedIn) {
      logger.warn('未登录，请先执行 get-qrcode 登录');
      return {
        success: false,
        error: 'NOT_LOGGED_IN',
        message: '未登录，请先执行 get-qrcode 登录',
      };
    }
    
    logger.info('导航到发布页面...');
    await page.goto(PUBLISH_URL, { waitUntil: 'domcontentloaded' });
    await randomSleep(2000, 3000);
    
    logger.info('点击上传视频...');
    
    const videoTabSelectors = [
      'text=上传视频',
      'text=视频',
      '[class*="video-tab"]',
      '[class*="upload-video"]',
    ];
    
    for (const selector of videoTabSelectors) {
      const videoTab = await page.$(selector);
      if (videoTab) {
        await videoTab.click();
        logger.info('已切换到视频上传');
        await randomSleep(1000, 2000);
        break;
      }
    }
    
    logger.info('上传视频文件...');
    const fileInput = await page.$('input[type="file"][accept*="video"], input[type="file"]');
    
    if (!fileInput) {
      throw new Error('未找到视频上传按钮');
    }
    
    await fileInput.setInputFiles(video);
    logger.info('视频文件已选择，等待上传...');
    
    await randomSleep(10000, 15000);
    
    let uploadComplete = false;
    let checkCount = 0;
    const maxChecks = 60;
    
    while (!uploadComplete && checkCount < maxChecks) {
      await randomSleep(3000, 5000);
      checkCount++;
      
      const pageContent = await page.content();
      
      if (pageContent.includes('上传成功') || pageContent.includes('上传完成')) {
        uploadComplete = true;
        logger.info('视频上传成功');
        break;
      }
      
      if (pageContent.includes('上传失败')) {
        throw new Error('视频上传失败');
      }
      
      logger.info(`等待视频上传... (${checkCount}/${maxChecks})`);
    }
    
    if (!uploadComplete) {
      logger.warn('视频上传超时，继续尝试发布...');
    }
    
    if (cover) {
      logger.info('上传封面图片...');
      const coverInput = await page.$('input[type="file"][accept*="image"]');
      
      if (coverInput) {
        await coverInput.setInputFiles(cover);
        logger.info('封面图片已上传');
        await randomSleep(2000, 3000);
      }
    }
    
    logger.info('填写标题...');
    const titleSelectors = [
      'input[placeholder*="填写标题"]',
      '.title-input input',
      'input[class*="title"]',
    ];
    
    let titleInput = null;
    for (const selector of titleSelectors) {
      titleInput = await page.$(selector);
      if (titleInput) break;
    }
    
    if (titleInput) {
      await titleInput.fill(title);
      logger.info('标题已填写');
    }
    
    await randomSleep(500, 1000);
    
    logger.info('填写正文...');
    const contentSelectors = [
      '.ql-editor',
      '[contenteditable="true"]',
      '.content-editor',
    ];
    
    let contentEditor = null;
    for (const selector of contentSelectors) {
      contentEditor = await page.$(selector);
      if (contentEditor) break;
    }
    
    if (contentEditor) {
      await contentEditor.click();
      await page.keyboard.type(content, { delay: 50 });
      logger.info('正文已填写');
    }
    
    if (tags.length > 0) {
      logger.info('添加话题标签...');
      
      for (const tag of tags) {
        try {
          const tagInput = await page.$('input[placeholder*="话题"], input[placeholder*="标签"]');
          
          if (tagInput) {
            await tagInput.fill(`#${tag}`);
            await randomSleep(500, 1000);
            await page.keyboard.press('Enter');
            logger.info(`已添加话题: #${tag}`);
          }
        } catch (e) {
          logger.warn(`添加话题失败: ${tag}`);
        }
      }
    }
    
    await randomSleep(1000, 2000);
    
    logger.info('点击发布按钮...');
    const publishBtn = await page.$('button:has-text("发布"), .publish-btn, button[class*="publish"]');
    
    if (!publishBtn) {
      throw new Error('未找到发布按钮');
    }
    
    await publishBtn.click();
    logger.info('已点击发布');
    
    await randomSleep(5000, 8000);
    
    const pageContent = await page.content();
    
    if (pageContent.includes('发布成功') || pageContent.includes('已发布')) {
      logger.info('视频笔记发布成功！');
      
      return {
        success: true,
        message: '视频笔记发布成功',
      };
    }
    
    const currentUrl = page.url();
    if (currentUrl.includes('/note/') || currentUrl.includes('/explore/')) {
      const match = currentUrl.match(/\/(note|explore)\/(\w+)/);
      const noteId = match ? match[2] : null;
      
      logger.info('视频笔记发布成功！');
      
      return {
        success: true,
        noteId,
        message: '视频笔记发布成功',
      };
    }
    
    return {
      success: true,
      message: '发布请求已提交，请手动检查结果',
    };
    
  } catch (error) {
    logger.error('发布失败:', error.message);
    
    return {
      success: false,
      error: error.message,
      message: '视频笔记发布失败',
    };
  }
}

async function main() {
  const args = process.argv.slice(2);
  
  const params = {};
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--title' && args[i + 1]) {
      params.title = args[i + 1];
      i++;
    } else if (args[i] === '--content' && args[i + 1]) {
      params.content = args[i + 1];
      i++;
    } else if (args[i] === '--video' && args[i + 1]) {
      params.video = args[i + 1];
      i++;
    } else if (args[i] === '--cover' && args[i + 1]) {
      params.cover = args[i + 1];
      i++;
    } else if (args[i] === '--tags' && args[i + 1]) {
      params.tags = args[i + 1].split(',').map(t => t.trim());
      i++;
    }
  }
  
  if (!params.title || !params.content || !params.video) {
    console.log('Usage: node publish-video.js --title "标题" --content "内容" --video "/path/video.mp4" [--cover "/path/cover.jpg"] [--tags "标签1,标签2"]');
    process.exit(1);
  }
  
  const result = await publishVideo(params);
  
  console.log('\n' + '='.repeat(50));
  
  if (result.success) {
    console.log('✅', result.message);
    if (result.noteId) {
      console.log(`笔记ID: ${result.noteId}`);
    }
  } else {
    console.log('❌', result.message);
    console.log(`错误: ${result.error}`);
  }
  
  console.log('='.repeat(50) + '\n');
  
  process.exit(result.success ? 0 : 1);
}

if (require.main === module) {
  main();
}

module.exports = { publishVideo };
