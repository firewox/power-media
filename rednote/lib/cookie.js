/**
 * Cookie 持久化管理模块
 * 
 * 管理 Cookie 的保存、加载和清除
 * 与 BrowserManager 配合使用，实现登录状态持久化
 */

const fs = require('fs');
const path = require('path');

/**
 * Cookie 管理器类
 * 
 * 使用方式：
 * ```javascript
 * const cookieManager = new CookieManager('/path/to/data');
 * 
 * // 保存 cookies
 * await cookieManager.save(cookies);
 * 
 * // 加载 cookies
 * const cookies = await cookieManager.load();
 * 
 * // 清除 cookies
 * await cookieManager.clear();
 * ```
 */
class CookieManager {
  /**
   * @param {string} dataPath - 数据存储路径
   */
  constructor(dataPath) {
    this.dataPath = dataPath;
    this.cookieFile = path.join(dataPath, 'cookies.json');
    this.stateFile = path.join(dataPath, 'login-state.json');
  }

  /**
   * 确保数据目录存在
   */
  ensureDataDir() {
    if (!fs.existsSync(this.dataPath)) {
      fs.mkdirSync(this.dataPath, { recursive: true });
    }
  }

  /**
   * 保存 Cookies 到文件
   * 
   * @param {Array} cookies - Cookie 数组（Playwright 格式）
   * @returns {Promise<{success: boolean, count: number}>}
   */
  async save(cookies) {
    this.ensureDataDir();

    if (!cookies || !Array.isArray(cookies)) {
      console.log('[Cookie] 无效的 cookies 数据');
      return { success: false, count: 0 };
    }

    try {
      const data = {
        cookies,
        savedAt: new Date().toISOString(),
        count: cookies.length,
      };

      fs.writeFileSync(
        this.cookieFile,
        JSON.stringify(data, null, 2),
        'utf-8'
      );

      console.log(`[Cookie] 已保存 ${cookies.length} 个 cookies`);
      return { success: true, count: cookies.length };
    } catch (error) {
      console.error('[Cookie] 保存失败:', error.message);
      return { success: false, count: 0, error: error.message };
    }
  }

  /**
   * 从文件加载 Cookies
   * 
   * @returns {Promise<Array>} Cookie 数组
   */
  async load() {
    if (!fs.existsSync(this.cookieFile)) {
      console.log('[Cookie] Cookie 文件不存在');
      return [];
    }

    try {
      const data = JSON.parse(fs.readFileSync(this.cookieFile, 'utf-8'));
      const cookies = data.cookies || [];

      console.log(`[Cookie] 已加载 ${cookies.length} 个 cookies`);
      console.log(`[Cookie] 保存时间: ${data.savedAt || '未知'}`);

      return cookies;
    } catch (error) {
      console.error('[Cookie] 加载失败:', error.message);
      return [];
    }
  }

  /**
   * 清除 Cookies
   * 
   * @returns {Promise<{success: boolean}>}
   */
  async clear() {
    try {
      if (fs.existsSync(this.cookieFile)) {
        fs.unlinkSync(this.cookieFile);
        console.log('[Cookie] Cookie 文件已删除');
      }

      if (fs.existsSync(this.stateFile)) {
        fs.unlinkSync(this.stateFile);
        console.log('[Cookie] 登录状态文件已删除');
      }

      // 清除浏览器数据目录
      const browserDataPath = path.join(this.dataPath, 'browser-data');
      if (fs.existsSync(browserDataPath)) {
        fs.rmSync(browserDataPath, { recursive: true, force: true });
        console.log('[Cookie] 浏览器数据已清除');
      }

      return { success: true };
    } catch (error) {
      console.error('[Cookie] 清除失败:', error.message);
      return { success: false, error: error.message };
    }
  }

  /**
   * 检查 Cookie 文件是否存在
   * 
   * @returns {boolean}
   */
  exists() {
    return fs.existsSync(this.cookieFile);
  }

  /**
   * 获取 Cookie 信息
   * 
   * @returns {object|null}
   */
  getInfo() {
    if (!this.exists()) {
      return null;
    }

    try {
      const data = JSON.parse(fs.readFileSync(this.cookieFile, 'utf-8'));
      return {
        count: data.count || 0,
        savedAt: data.savedAt || null,
      };
    } catch {
      return null;
    }
  }

  /**
   * 保存登录状态
   * 
   * @param {object} state - 登录状态
   * @param {boolean} state.isLoggedIn - 是否已登录
   * @param {string} state.username - 用户名
   * @param {string} state.userId - 用户 ID
   */
  async saveLoginState(state) {
    this.ensureDataDir();

    const data = {
      ...state,
      updatedAt: new Date().toISOString(),
    };

    fs.writeFileSync(this.stateFile, JSON.stringify(data, null, 2), 'utf-8');
    console.log('[Cookie] 登录状态已保存');
  }

  /**
   * 加载登录状态
   * 
   * @returns {object|null}
   */
  loadLoginState() {
    if (!fs.existsSync(this.stateFile)) {
      return null;
    }

    try {
      return JSON.parse(fs.readFileSync(this.stateFile, 'utf-8'));
    } catch {
      return null;
    }
  }

  /**
   * 检查是否已登录（基于缓存的登录状态）
   * 
   * @returns {boolean}
   */
  isLoggedIn() {
    const state = this.loadLoginState();
    return state?.isLoggedIn === true;
  }

  /**
   * 从浏览器上下文提取关键 Cookies
   * 
   * @param {Array} cookies - Playwright cookies
   * @returns {object} 关键 cookie 键值对
   */
  extractKeyCookies(cookies) {
    const keyNames = ['a1', 'webId', 'web_session', 'websectiga', 'sec_poison_id'];
    const result = {};

    for (const cookie of cookies) {
      if (keyNames.includes(cookie.name)) {
        result[cookie.name] = cookie.value;
      }
    }

    return result;
  }

  /**
   * 验证 Cookie 有效性（检查关键 cookie 是否存在）
   * 
   * @param {Array} cookies - Cookie 数组
   * @returns {{valid: boolean, missing: string[]}}
   */
  validateCookies(cookies) {
    const requiredCookies = ['a1', 'webId', 'web_session'];
    const existingNames = cookies.map(c => c.name);
    const missing = requiredCookies.filter(name => !existingNames.includes(name));

    return {
      valid: missing.length === 0,
      missing,
    };
  }
}

/**
 * 从浏览器上下文同步 Cookies 到文件
 * 
 * @param {import('playwright').BrowserContext} context - Playwright 浏览器上下文
 * @param {CookieManager} cookieManager - Cookie 管理器
 */
async function syncCookiesFromContext(context, cookieManager) {
  const cookies = await context.cookies();
  await cookieManager.save(cookies);
  
  // 保存关键 cookie 信息
  const keyCookies = cookieManager.extractKeyCookies(cookies);
  console.log('[Cookie] 关键 cookies:', keyCookies);
  
  return cookies;
}

/**
 * 将 Cookies 加载到浏览器上下文
 * 
 * @param {import('playwright').BrowserContext} context - Playwright 浏览器上下文
 * @param {CookieManager} cookieManager - Cookie 管理器
 */
async function loadCookiesToContext(context, cookieManager) {
  const cookies = await cookieManager.load();
  
  if (cookies.length > 0) {
    await context.addCookies(cookies);
    console.log(`[Cookie] 已将 ${cookies.length} 个 cookies 加载到上下文`);
  }
  
  return cookies;
}

module.exports = {
  CookieManager,
  syncCookiesFromContext,
  loadCookiesToContext,
};
