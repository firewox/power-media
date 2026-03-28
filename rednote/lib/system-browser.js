const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const { spawn, exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

const SYSTEM_BROWSER_PATHS = {
  win32: [
    { name: 'edge', path: () => path.join(process.env['ProgramFiles(x86)'] || process.env.ProgramFiles, 'Microsoft', 'Edge', 'Application', 'msedge.exe') },
    { name: 'edge', path: () => path.join(process.env.LOCALAPPDATA, 'Microsoft', 'Edge', 'Application', 'msedge.exe') },
    { name: 'chrome', path: () => path.join(process.env['ProgramFiles(x86)'] || process.env.ProgramFiles, 'Google', 'Chrome', 'Application', 'chrome.exe') },
    { name: 'chrome', path: () => path.join(process.env.LOCALAPPDATA, 'Google', 'Chrome', 'Application', 'chrome.exe') },
  ],
  darwin: [
    { name: 'chrome', path: () => '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' },
    { name: 'edge', path: () => '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge' },
  ],
  linux: [
    { name: 'chrome', path: () => '/usr/bin/google-chrome' },
    { name: 'chrome', path: () => '/usr/bin/google-chrome-stable' },
    { name: 'edge', path: () => '/usr/bin/microsoft-edge' },
    { name: 'chromium', path: () => '/usr/bin/chromium' },
  ],
};

function getSystemBrowser() {
  const platform = process.platform;
  const paths = SYSTEM_BROWSER_PATHS[platform] || SYSTEM_BROWSER_PATHS.linux;
  
  for (const { name, path: getPath } of paths) {
    const browserPath = getPath();
    if (fs.existsSync(browserPath)) {
      return { executablePath: browserPath, name };
    }
  }
  
  return null;
}

async function isBrowserRunning(browserName) {
  try {
    const processName = browserName === 'edge' ? 'msedge' : 'chrome';
    if (process.platform === 'win32') {
      const { stdout } = await execPromise(`tasklist /FI "IMAGENAME eq ${processName}.exe"`);
      return stdout.includes(`${processName}.exe`);
    } else {
      const { stdout } = await execPromise(`pgrep -x "${processName}"`);
      return stdout.trim().length > 0;
    }
  } catch (e) {
    return false;
  }
}

async function killBrowser(browserName) {
  try {
    const processName = browserName === 'edge' ? 'msedge' : 'chrome';
    if (process.platform === 'win32') {
      await execPromise(`taskkill /F /IM ${processName}.exe`);
    } else {
      await execPromise(`pkill -9 "${processName}"`);
    }
    console.log(`[Browser] 已关闭运行中的 ${browserName}`);
    await new Promise(r => setTimeout(r, 2000));
  } catch (e) {
    // Browser not running or couldn't kill
  }
}

async function findExistingCDPPort(browserName) {
  try {
    const processName = browserName === 'edge' ? 'msedge' : 'chrome';
    if (process.platform === 'win32') {
      const { stdout } = await execPromise(`wmic process where "name='${processName}.exe'" get CommandLine /format:list`);
      const lines = stdout.split('\n');
      for (const line of lines) {
        if (line.includes('--remote-debugging-port=')) {
          const match = line.match(/--remote-debugging-port=(\d+)/);
          if (match) return parseInt(match[1], 10);
        }
      }
    } else {
      const { stdout } = await execPromise(`ps aux | grep "${processName}" | grep remote-debugging`);
      const match = stdout.match(/--remote-debugging-port=(\d+)/);
      if (match) return parseInt(match[1], 10);
    }
  } catch (e) {
    // Not found
  }
  return null;
}

async function testCDPConnection(port) {
  try {
    const http = require('http');
    await new Promise((resolve, reject) => {
      const req = http.get(`http://localhost:${port}/json/version`, (res) => {
        if (res.statusCode === 200) resolve();
        else reject(new Error('Invalid response'));
      });
      req.on('error', reject);
      req.setTimeout(2000, () => {
        req.destroy();
        reject(new Error('Timeout'));
      });
    });
    return true;
  } catch (e) {
    return false;
  }
}

async function findAvailablePort(start, end) {
  const net = require('net');
  for (let port = start; port <= end; port++) {
    try {
      await new Promise((resolve, reject) => {
        const server = net.createServer();
        server.listen(port, () => {
          server.close(() => resolve(port));
        });
        server.on('error', reject);
      });
      return port;
    } catch (e) {
      continue;
    }
  }
  throw new Error('未找到可用端口');
}

class SystemBrowserManager {
  constructor(options = {}) {
    this.options = {
      headless: false,
      width: 1280,
      height: 720,
      timeout: 60000,
      killExisting: options.killExisting !== false,
      ...options,
    };
    
    this.browser = null;
    this.context = null;
    this.page = null;
    this.isLaunched = false;
    this.systemBrowser = null;
    this.cdpPort = null;
    this.browserProcess = null;
  }

  async launch() {
    if (this.isLaunched) return;

    console.log('[Browser] 启动系统浏览器...');
    
    this.systemBrowser = getSystemBrowser();
    if (!this.systemBrowser) {
      throw new Error('未找到系统浏览器 (Edge 或 Chrome)');
    }
    
    console.log(`[Browser] 找到: ${this.systemBrowser.name}`);
    console.log(`[Browser] 路径: ${this.systemBrowser.executablePath}`);
    
    // Check if browser is already running
    const isRunning = await isBrowserRunning(this.systemBrowser.name);
    
    if (isRunning) {
      console.log(`[Browser] 检测到 ${this.systemBrowser.name} 已在运行`);
      
      // Check if CDP is available
      const existingPort = await findExistingCDPPort(this.systemBrowser.name);
      if (existingPort && await testCDPConnection(existingPort)) {
        console.log(`[Browser] 发现现有 CDP 端口: ${existingPort}`);
        this.cdpPort = existingPort;
      } else {
        console.log('[Browser] 现有实例未启用 CDP');
        
        if (this.options.killExisting) {
          await killBrowser(this.systemBrowser.name);
        } else {
          throw new Error(`${this.systemBrowser.name} 已在运行但未启用 CDP。请关闭浏览器后重试，或设置 killExisting: true`);
        }
      }
    }
    
    // Get system user data directory
    const userDataDir = getSystemUserDataDir(this.systemBrowser.name);
    if (userDataDir) {
      console.log(`[Browser] 用户数据目录: ${userDataDir}`);
    }
    
    // If no CDP port, start browser with CDP
    if (!this.cdpPort) {
      this.cdpPort = await findAvailablePort(9222, 9333);
      console.log(`[Browser] CDP 端口: ${this.cdpPort}`);
      
      const args = [
        `--remote-debugging-port=${this.cdpPort}`,
        '--no-first-run',
        '--no-default-browser-check',
      ];
      
      // Use system user data directory to preserve login state
      if (userDataDir && fs.existsSync(userDataDir)) {
        args.push(`--user-data-dir=${userDataDir}`);
      }
      
      console.log(`[Browser] 启动参数: ${args.join(' ')}`);
      
      this.browserProcess = spawn(this.systemBrowser.executablePath, args, {
        detached: true,
        stdio: 'ignore',
      });
      
      this.browserProcess.unref();
      
      console.log('[Browser] 等待浏览器启动...');
      await this.waitForBrowser(this.cdpPort, 15000);
    }
    
    // Connect via CDP
    console.log(`[Browser] 通过 CDP 连接到端口 ${this.cdpPort}...`);
    this.browser = await chromium.connectOverCDP(`http://localhost:${this.cdpPort}`);
    
    // Get or create context
    const contexts = this.browser.contexts();
    if (contexts.length > 0) {
      this.context = contexts[0];
      console.log('[Browser] 复用已有上下文');
    } else {
      this.context = await this.browser.newContext({
        viewport: { width: this.options.width, height: this.options.height },
      });
      console.log('[Browser] 创建新上下文');
    }
    
    // Create new page (opens in new window/tab)
    this.page = await this.context.newPage();
    console.log('[Browser] 创建新页面');
    
    this.page.setDefaultTimeout(this.options.timeout);
    this.page.setDefaultNavigationTimeout(this.options.timeout);
    
    this.isLaunched = true;
    console.log('[Browser] ✅ 浏览器启动成功');
    console.log('[Browser] ✅ 已复用系统浏览器登录态');
  }
  
  async waitForBrowser(port, timeout) {
    const start = Date.now();
    while (Date.now() - start < timeout) {
      if (await testCDPConnection(port)) {
        return;
      }
      await new Promise(r => setTimeout(r, 500));
    }
    throw new Error('浏览器启动超时');
  }

  async getPage() {
    if (!this.isLaunched) {
      await this.launch();
    }
    return this.page;
  }

  async goto(url, options = {}) {
    const page = await this.getPage();
    console.log(`[Browser] 导航到: ${url}`);
    await page.goto(url, {
      waitUntil: options.waitUntil ?? 'domcontentloaded',
      timeout: options.timeout ?? this.options.timeout,
    });
  }

  async close() {
    if (this.browser) {
      console.log('[Browser] 断开连接...');
      await this.browser.close();
      this.browser = null;
      this.context = null;
      this.page = null;
    }
    this.isLaunched = false;
    console.log('[Browser] 已断开');
  }
}

function getSystemUserDataDir(browserName) {
  const platform = process.platform;
  const localAppData = process.env.LOCALAPPDATA;
  const homeDir = process.env.HOME || process.env.USERPROFILE;
  
  if (platform === 'win32') {
    if (browserName === 'edge') {
      return path.join(localAppData, 'Microsoft', 'Edge', 'User Data');
    } else if (browserName === 'chrome') {
      return path.join(localAppData, 'Google', 'Chrome', 'User Data');
    }
  } else if (platform === 'darwin') {
    if (browserName === 'edge') {
      return path.join(homeDir, 'Library', 'Application Support', 'Microsoft Edge');
    } else if (browserName === 'chrome') {
      return path.join(homeDir, 'Library', 'Application Support', 'Google', 'Chrome');
    }
  } else {
    if (browserName === 'edge') {
      return path.join(homeDir, '.config', 'microsoft-edge');
    } else if (browserName === 'chrome') {
      return path.join(homeDir, '.config', 'google-chrome');
    }
  }
  
  return null;
}

module.exports = {
  SystemBrowserManager,
  getSystemBrowser,
  getSystemUserDataDir,
  isBrowserRunning,
  killBrowser,
};
