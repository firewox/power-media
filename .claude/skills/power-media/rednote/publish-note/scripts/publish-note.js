#!/usr/bin/env node

const path = require('path');
const fs = require('fs');

const libPath = path.join(__dirname, '..', '..', 'lib');
const { getBrowserManager, closeAll } = require(path.join(libPath, 'browser'));
const { CookieManager, syncCookiesFromContext } = require(path.join(libPath, 'cookie'));
const { logger, randomSleep, validateParams, retry } = require(path.join(libPath, 'utils'));

const DATA_PATH = process.env.XHS_DATA_PATH || path.join(__dirname, '..', '..', 'data');
const PUBLISH_URL = 'https://creator.xiaohongshu.com/publish/publish?source=official';

const SELECTORS = {
  uploadBtn: '.upload-input, input[type="file"]',
  titleInput: '.title-input, input[placeholder*="标题"], .d-input input',
  contentEditor: '.content-input, .ql-editor, [contenteditable="true"]',
  tagInput: '.tag-input, input[placeholder*="话题"]',
  tagItem: '.tag-item',
  publishBtn: '.publish-btn, button:has-text("发布")',
  successTip: '.success-tip, .publish-success',
};

const LIMITS = {
  titleMax: 20,
  contentMax: 1000,
  imageMax: 18,
  tagMax: 10,
};

function validateInput(params) {
  const { title, content, images } = params;
  
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
  
  if (!images || !Array.isArray(images) || images.length === 0) {
    throw new Error('至少需要上传一张图片');
  }
  if (images.length > LIMITS.imageMax) {
    throw new Error(`最多上传 ${LIMITS.imageMax} 张图片`);
  }
  
  for (const imgPath of images) {
    if (!fs.existsSync(imgPath)) {
      throw new Error(`图片不存在: ${imgPath}`);
    }
  }
  
  if (params.tags && params.tags.length > LIMITS.tagMax) {
    throw new Error(`最多添加 ${LIMITS.tagMax} 个话题标签`);
  }
  
  return true;
}

async function publishNote(params) {
  const { title, content, images, tags = [], visibility = 'public', isOriginal = true, scheduleAt } = params;
  const dataPath = params.dataPath || DATA_PATH;
  
  validateInput(params);
  
  logger.info('发布图文笔记...');
  logger.info(`标题: ${title}`);
  logger.info(`图片数量: ${images.length}`);
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
    
    logger.info('上传图片...');
    const fileInput = await page.$('input[type="file"]');
    
    if (!fileInput) {
      throw new Error('未找到图片上传按钮');
    }
    
    await fileInput.setInputFiles(images);
    logger.info(`已上传 ${images.length} 张图片`);
    
    await randomSleep(3000, 5000);
    
    logger.info('填写标题...');
    const titleSelectors = [
      'input[placeholder*="填写标题"]',
      '.title-input input',
      '.c-input__inner',
      'input[class*="title"]',
    ];
    
    let titleInput = null;
    for (const selector of titleSelectors) {
      titleInput = await page.$(selector);
      if (titleInput) break;
    }
    
    if (!titleInput) {
      logger.warn('未找到标题输入框，尝试点击编辑区域');
      const editorArea = await page.$('.editor-area, .publish-editor, [class*="editor"]');
      if (editorArea) {
        await editorArea.click();
        await randomSleep(500, 1000);
      }
      
      for (const selector of titleSelectors) {
        titleInput = await page.$(selector);
        if (titleInput) break;
      }
    }
    
    if (titleInput) {
      await titleInput.fill(title);
      logger.info('标题已填写');
    } else {
      logger.warn('未找到标题输入框，跳过');
    }
    
    await randomSleep(500, 1000);
    
    logger.info('填写正文...');
    const contentSelectors = [
      '.ql-editor',
      '[contenteditable="true"]',
      '.content-editor',
      '.c-textarea__inner',
      'div[contenteditable="true"]',
    ];
    
    let contentEditor = null;
    for (const selector of contentSelectors) {
      contentEditor = await page.$(selector);
      if (contentEditor) break;
    }
    
    if (contentEditor) {
      await contentEditor.click();
      await randomSleep(300, 500);
      
      await page.keyboard.type(content, { delay: 50 });
      logger.info('正文已填写');
    } else {
      logger.warn('未找到正文编辑框');
    }
    
    if (tags.length > 0) {
      logger.info('添加话题标签...');
      
      for (const tag of tags) {
        try {
          const tagInputSelectors = [
            'input[placeholder*="话题"]',
            'input[placeholder*="标签"]',
            '.tag-input input',
          ];
          
          let tagInput = null;
          for (const selector of tagInputSelectors) {
            tagInput = await page.$(selector);
            if (tagInput) break;
          }
          
          if (tagInput) {
            await tagInput.fill(`#${tag}`);
            await randomSleep(500, 1000);
            
            await page.keyboard.press('Enter');
            logger.info(`已添加话题: #${tag}`);
            await randomSleep(300, 500);
          }
        } catch (e) {
          logger.warn(`添加话题失败: ${tag}`, e.message);
        }
      }
    }
    
    await randomSleep(1000, 2000);
    
    logger.info('点击发布按钮...');
    const publishSelectors = [
      'button:has-text("发布")',
      '.publish-btn',
      'button[class*="publish"]',
      '.btn-publish',
    ];
    
    let publishBtn = null;
    for (const selector of publishSelectors) {
      publishBtn = await page.$(selector);
      if (publishBtn) break;
    }
    
    if (!publishBtn) {
      throw new Error('未找到发布按钮');
    }
    
    await publishBtn.click();
    logger.info('已点击发布');
    
    await randomSleep(3000, 5000);
    
    const currentUrl = page.url();
    let noteId = null;
    
    if (currentUrl.includes('/note/') || currentUrl.includes('/explore/')) {
      const match = currentUrl.match(/\/(note|explore)\/(\w+)/);
      if (match) {
        noteId = match[2];
      }
    }
    
    const successIndicators = [
      '.success-tip',
      '.publish-success',
      '[class*="success"]',
    ];
    
    let publishSuccess = false;
    for (const selector of successIndicators) {
      const el = await page.$(selector);
      if (el) {
        publishSuccess = true;
        break;
      }
    }
    
    if (publishSuccess || noteId) {
      logger.info('笔记发布成功！');
      
      return {
        success: true,
        noteId,
        message: '笔记发布成功',
      };
    }
    
    const pageContent = await page.content();
    if (pageContent.includes('发布成功') || pageContent.includes('已发布')) {
      logger.info('检测到发布成功提示');
      return {
        success: true,
        message: '笔记发布成功',
      };
    }
    
    logger.warn('无法确认发布状态，请手动检查');
    
    return {
      success: true,
      message: '发布请求已提交，请手动检查结果',
    };
    
  } catch (error) {
    logger.error('发布失败:', error.message);
    
    return {
      success: false,
      error: error.message,
      message: '笔记发布失败',
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
    } else if (args[i] === '--images' && args[i + 1]) {
      params.images = args[i + 1].split(',').map(p => p.trim());
      i++;
    } else if (args[i] === '--tags' && args[i + 1]) {
      params.tags = args[i + 1].split(',').map(t => t.trim());
      i++;
    }
  }
  
  if (!params.title || !params.content || !params.images) {
    console.log('Usage: node publish-note.js --title "标题" --content "内容" --images "/path/1.jpg,/path/2.jpg" [--tags "标签1,标签2"]');
    process.exit(1);
  }
  
  const result = await publishNote(params);
  
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

module.exports = { publishNote };
