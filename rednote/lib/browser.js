/**
 * 浏览器管理模块
 * 
 * 使用 Playwright 封装浏览器操作，支持：
 * - 持久化上下文（Cookie 自动保存）
 * - 非无头模式（小红书需要）
 * - 单例模式管理浏览器实例
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

/**
 * 浏览器管理器类
 * 
 * 使用方式：
 * ```javascript
 * const browserManager = new BrowserManager('/path/to/data');
 * const page = await browserManager.getPage();
 * // 使用 page 进行操作...
 * await browserManager.close();
 * ```
 */
class BrowserManager {
  /**
   * @param {string} dataPath - 数据存储路径（用于保存 Cookie 等）
   * @param {object} options - 配置选项
   * @param {boolean} options.headless - 是否无头模式，默认 false（小红书需要非无头）
   * @param {number} options.width - 视口宽度，默认 1280
   * @param {number} options.height - 视口高度，默认 720
   */
  constructor(dataPath, options = {}) {
    this.dataPath = dataPath;
    this.browserDataPath = path.join(dataPath, 'browser-data');
    this.options = {
      headless: options.headless ?? false,
      width: options.width ?? 1280,
      height: options.height ?? 720,
      timeout: options.timeout ?? 60000,
    };
    
    this.context = null;
    this.page = null;
    this.isLaunched = false;
  }

  /**
   * 确保数据目录存在
   */
  ensureDataDir() {
    if (!fs.existsSync(this.dataPath)) {
      fs.mkdirSync(this.dataPath, { recursive: true });
    }
    if (!fs.existsSync(this.browserDataPath)) {
      fs.mkdirSync(this.browserDataPath, { recursive: true });
    }
  }

  /**
   * 启动浏览器（持久化上下文）
   * 
   * @returns {Promise<void>}
   */
  async launch() {
    if (this.isLaunched) {
      return;
    }

    this.ensureDataDir();

    console.log('[Browser] 启动浏览器...');
    console.log(`[Browser] 数据路径: ${this.browserDataPath}`);
    console.log(`[Browser] 无头模式: ${this.options.headless}`);

    // 使用持久化上下文启动浏览器
    // 这样 Cookie 会自动保存到 browserDataPath 目录
    this.context = await chromium.launchPersistentContext(
      this.browserDataPath,
      {
        headless: this.options.headless,
        viewport: {
          width: this.options.width,
          height: this.options.height,
        },
        // 设置 User-Agent 避免被检测
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        // 忽略 HTTPS 错误
        ignoreHTTPSErrors: true,
        // 禁用一些自动化检测特征
        args: [
          '--disable-blink-features=AutomationControlled',
          '--disable-web-security',
          '--disable-features=IsolateOrigins,site-per-process',
        ],
        // 设置默认超时
        timeout: this.options.timeout,
      }
    );

    // 获取或创建页面
    const pages = this.context.pages();
    if (pages.length > 0) {
      this.page = pages[0];
    } else {
      this.page = await this.context.newPage();
    }

    // 设置默认超时
    this.page.setDefaultTimeout(this.options.timeout);
    this.page.setDefaultNavigationTimeout(this.options.timeout);

    this.isLaunched = true;
    console.log('[Browser] 浏览器启动成功');
  }

  /**
   * 获取页面实例
   * 
   * @returns {Promise<import('playwright').Page>}
   */
  async getPage() {
    if (!this.isLaunched) {
      await this.launch();
    }
    return this.page;
  }

  /**
   * 获取浏览器上下文
   * 
   * @returns {import('playwright').BrowserContext|null}
   */
  getContext() {
    return this.context;
  }

  /**
   * 导航到指定 URL
   * 
   * @param {string} url - 目标 URL
   * @param {object} options - 导航选项
   * @returns {Promise<void>}
   */
  async goto(url, options = {}) {
    const page = await this.getPage();
    console.log(`[Browser] 导航到: ${url}`);
    await page.goto(url, {
      waitUntil: options.waitUntil ?? 'domcontentloaded',
      timeout: options.timeout ?? this.options.timeout,
    });
  }

  /**
   * 等待页面稳定
   * 
   * @param {number} timeout - 超时时间（毫秒）
   * @returns {Promise<void>}
   */
  async waitForStable(timeout = 3000) {
    const page = await this.getPage();
    await page.waitForTimeout(timeout);
  }

  /**
   * 检查是否已启动
   * 
   * @returns {boolean}
   */
  isRunning() {
    return this.isLaunched && this.context !== null;
  }

  /**
   * 关闭浏览器
   */
  async close() {
    if (this.context) {
      console.log('[Browser] 关闭浏览器...');
      await this.context.close();
      this.context = null;
      this.page = null;
      this.isLaunched = false;
      console.log('[Browser] 浏览器已关闭');
    }
  }

  /**
   * 截图
   * 
   * @param {string} outputPath - 输出路径
   * @returns {Promise<Buffer>}
   */
  async screenshot(outputPath) {
    const page = await this.getPage();
    return await page.screenshot({ path: outputPath, fullPage: true });
  }

  /**
   * 执行 JavaScript
   * 
   * @param {string} script - JavaScript 代码
   * @param {*} arg - 参数
   * @returns {Promise<*>}
   */
  async evaluate(script, arg) {
    const page = await this.getPage();
    return await page.evaluate(script, arg);
  }
}

// 单例实例缓存
const instances = new Map();

/**
 * 获取或创建浏览器管理器实例（单例模式）
 * 
 * @param {string} dataPath - 数据存储路径
 * @param {object} options - 配置选项
 * @returns {BrowserManager}
 */
function getBrowserManager(dataPath, options = {}) {
  if (!instances.has(dataPath)) {
    instances.set(dataPath, new BrowserManager(dataPath, options));
  }
  return instances.get(dataPath);
}

/**
 * 关闭所有浏览器实例
 */
async function closeAll() {
  for (const instance of instances.values()) {
    await instance.close();
  }
  instances.clear();
}

module.exports = {
  BrowserManager,
  getBrowserManager,
  closeAll,
};
