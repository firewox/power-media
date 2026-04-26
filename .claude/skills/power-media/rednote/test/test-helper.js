/**
 * 测试辅助工具
 * 
 * 提供测试数据管理、选择器验证等辅助功能
 */

const fs = require('fs');
const path = require('path');

const libPath = path.join(__dirname, '..', 'lib');
const { getBrowserManager } = require(path.join(libPath, 'browser'));
const { logger } = require(path.join(libPath, 'utils'));

const TestHelper = {
  /**
   * 从推荐列表获取有效的 noteId
   */
  async getValidNoteId(dataPath) {
    const { getFeeds } = require('../get-feeds/scripts/get-feeds');
    
    logger.info('获取有效 noteId...');
    
    const result = await getFeeds({ count: 5, dataPath });
    
    if (!result.success || result.feeds.length === 0) {
      throw new Error('无法从推荐列表获取 noteId');
    }
    
    const noteId = result.feeds[0].noteId;
    logger.info(`获取到 noteId: ${noteId}`);
    
    return noteId;
  },

  /**
   * 查找页面元素（多选择器策略）
   */
  async findElement(page, selectors, name) {
    logger.info(`查找 ${name}...`);
    
    const selectorList = Array.isArray(selectors) ? selectors : [selectors];
    
    for (const selector of selectorList) {
      try {
        const element = await page.$(selector);
        if (element) {
          logger.info(`✅ ${name} 找到: ${selector}`);
          return element;
        }
      } catch (e) {
        logger.debug(`  ${selector} 失败: ${e.message}`);
      }
    }
    
    logger.warn(`❌ ${name} 未找到，尝试的选择器: ${selectorList.join(', ')}`);
    return null;
  },

  /**
   * 等待元素出现
   */
  async waitForElement(page, selectors, name, timeout = 5000) {
    logger.info(`等待 ${name}...`);
    
    const selectorList = Array.isArray(selectors) ? selectors : [selectors];
    
    for (const selector of selectorList) {
      try {
        const element = await page.waitForSelector(selector, { timeout });
        if (element) {
          logger.info(`✅ ${name} 出现: ${selector}`);
          return element;
        }
      } catch (e) {
        logger.debug(`  ${selector} 超时`);
      }
    }
    
    logger.warn(`❌ ${name} 等待超时`);
    return null;
  },

  /**
   * 保存调试截图
   */
  async saveDebugScreenshot(page, name) {
    const debugDir = path.join(__dirname, '..', 'debug');
    if (!fs.existsSync(debugDir)) {
      fs.mkdirSync(debugDir, { recursive: true });
    }
    
    const filename = `${name}-${Date.now()}.png`;
    const filepath = path.join(debugDir, filename);
    
    await page.screenshot({ path: filepath, fullPage: true });
    logger.info(`📸 截图已保存: ${filepath}`);
    
    return filepath;
  },

  /**
   * 提取页面文本
   */
  async extractPageText(page) {
    return await page.evaluate(() => {
      return document.body.innerText.slice(0, 500);
    });
  },

  /**
   * 查找包含文本的元素
   */
  async findElementByText(page, text) {
    return await page.$eval(`text=${text}`, el => ({
      tag: el.tagName,
      class: el.className,
      id: el.id
    })).catch(() => null);
  }
};

module.exports = TestHelper;
