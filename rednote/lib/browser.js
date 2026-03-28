const { chromium, firefox } = require('playwright');
const path = require('path');
const fs = require('fs');

const BROWSER_TYPES = {
  chromium,
  firefox,
};

function getSystemBrowser() {
  const platform = process.platform;
  
  if (platform === 'win32') {
    const programFiles = process.env['ProgramFiles(x86)'] || process.env.ProgramFiles;
    const localAppData = process.env.LOCALAPPDATA;
    
    const possiblePaths = [
      path.join(programFiles, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
      path.join(localAppData, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
      path.join(programFiles, 'Google', 'Chrome', 'Application', 'chrome.exe'),
      path.join(localAppData, 'Google', 'Chrome', 'Application', 'chrome.exe'),
      path.join(localAppData, 'Google', 'Chrome Beta', 'Application', 'chrome.exe'),
      path.join(localAppData, 'Google', 'Chrome Dev', 'Application', 'chrome.exe'),
    ];
    
    for (const browserPath of possiblePaths) {
      if (fs.existsSync(browserPath)) {
        const isEdge = browserPath.includes('Edge');
        console.log(`[Browser] 找到系统浏览器: ${browserPath}`);
        return { 
          executablePath: browserPath, 
          type: 'chromium',
          name: isEdge ? 'edge' : 'chrome'
        };
      }
    }
  } else if (platform === 'darwin') {
    const possiblePaths = [
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
      '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
      '/Applications/Firefox.app/Contents/MacOS/firefox',
    ];
    
    for (const browserPath of possiblePaths) {
      if (fs.existsSync(browserPath)) {
        const isFirefox = browserPath.includes('Firefox');
        const isEdge = browserPath.includes('Edge');
        console.log(`[Browser] 找到系统浏览器: ${browserPath}`);
        return { 
          executablePath: browserPath, 
          type: isFirefox ? 'firefox' : 'chromium',
          name: isFirefox ? 'firefox' : (isEdge ? 'edge' : 'chrome')
        };
      }
    }
  } else {
    const possiblePaths = [
      '/usr/bin/google-chrome',
      '/usr/bin/google-chrome-stable',
      '/usr/bin/microsoft-edge',
      '/usr/bin/firefox',
      '/usr/bin/chromium',
      '/usr/bin/chromium-browser',
    ];
    
    for (const browserPath of possiblePaths) {
      if (fs.existsSync(browserPath)) {
        const isFirefox = browserPath.includes('firefox');
        const isEdge = browserPath.includes('edge');
        console.log(`[Browser] 找到系统浏览器: ${browserPath}`);
        return { 
          executablePath: browserPath, 
          type: isFirefox ? 'firefox' : 'chromium',
          name: isFirefox ? 'firefox' : (isEdge ? 'edge' : 'chrome')
        };
      }
    }
  }
  
  return null;
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

class BrowserManager {
  constructor(dataPath, options = {}) {
    this.dataPath = dataPath;
    this.browserDataPath = path.join(dataPath, 'browser-data');
    this.browserType = options.browserType || 'chromium';
    this.useSystemBrowser = options.useSystemBrowser !== false;
    this.useSystemProfile = options.useSystemProfile === true;
    this.executablePath = options.executablePath;
    this.userDataDir = options.userDataDir;
    this.profile = options.profile || 'Default';
    this.persistent = options.persistent ?? true;
    this.options = {
      headless: options.headless ?? false,
      width: options.width ?? 1280,
      height: options.height ?? 720,
      timeout: options.timeout ?? 60000,
    };
    
    this.browser = null;
    this.context = null;
    this.page = null;
    this.isLaunched = false;
    this.systemBrowser = null;
  }

  ensureDataDir() {
    if (!fs.existsSync(this.dataPath)) {
      fs.mkdirSync(this.dataPath, { recursive: true });
    }
    if (!fs.existsSync(this.browserDataPath)) {
      fs.mkdirSync(this.browserDataPath, { recursive: true });
    }
  }

  async launch() {
    if (this.isLaunched) {
      return;
    }

    this.ensureDataDir();

    console.log('[Browser] 启动浏览器...');
    
    let launchOptions = {
      headless: this.options.headless,
    };
    
    let userDataDir = this.browserDataPath;
    
    if (this.useSystemBrowser) {
      this.systemBrowser = getSystemBrowser();
      if (this.systemBrowser) {
        console.log(`[Browser] 使用系统浏览器: ${this.systemBrowser.name}`);
        launchOptions.executablePath = this.systemBrowser.executablePath;
        this.browserType = this.systemBrowser.type;
        
        if (this.useSystemProfile) {
          const systemUserData = getSystemUserDataDir(this.systemBrowser.name);
          if (systemUserData && fs.existsSync(systemUserData)) {
            console.log(`[Browser] 使用系统用户数据: ${systemUserData}`);
            console.log(`[Browser] 使用 Profile: ${this.profile}`);
            userDataDir = systemUserData;
            
            launchOptions.args = [
              `--profile-directory=${this.profile}`,
            ];
          } else {
            console.log(`[Browser] 未找到系统用户数据，使用独立数据目录`);
          }
        }
      } else {
        console.log('[Browser] 未找到系统浏览器，使用 Playwright 内置浏览器');
      }
    }
    
    if (this.executablePath) {
      launchOptions.executablePath = this.executablePath;
    }
    
    if (this.userDataDir) {
      userDataDir = this.userDataDir;
    }

    console.log(`[Browser] 浏览器类型: ${this.browserType}`);
    console.log(`[Browser] 数据目录: ${userDataDir}`);
    console.log(`[Browser] 无头模式: ${this.options.headless}`);

    const browserType = BROWSER_TYPES[this.browserType];
    if (!browserType) {
      throw new Error(`不支持的浏览器类型: ${this.browserType}`);
    }

    const contextOptions = {
      viewport: {
        width: this.options.width,
        height: this.options.height,
      },
      ignoreHTTPSErrors: true,
    };

    if (this.persistent) {
      this.context = await browserType.launchPersistentContext(
        userDataDir,
        {
          ...launchOptions,
          ...contextOptions,
        }
      );
    } else {
      this.browser = await browserType.launch(launchOptions);
      this.context = await this.browser.newContext(contextOptions);
    }

    const pages = this.context.pages();
    if (pages.length > 0) {
      this.page = pages[0];
    } else {
      this.page = await this.context.newPage();
    }

    this.page.setDefaultTimeout(this.options.timeout);
    this.page.setDefaultNavigationTimeout(this.options.timeout);

    this.isLaunched = true;
    console.log('[Browser] 浏览器启动成功');
  }

  async getPage() {
    if (!this.isLaunched) {
      await this.launch();
    }
    return this.page;
  }

  getContext() {
    return this.context;
  }

  async goto(url, options = {}) {
    const page = await this.getPage();
    console.log(`[Browser] 导航到: ${url}`);
    await page.goto(url, {
      waitUntil: options.waitUntil ?? 'domcontentloaded',
      timeout: options.timeout ?? this.options.timeout,
    });
  }

  async waitForStable(timeout = 3000) {
    const page = await this.getPage();
    await page.waitForTimeout(timeout);
  }

  isRunning() {
    return this.isLaunched && this.context !== null;
  }

  async close() {
    if (this.context) {
      console.log('[Browser] 关闭浏览器...');
      await this.context.close();
      this.context = null;
      this.page = null;
    }
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
    }
    this.isLaunched = false;
    console.log('[Browser] 浏览器已关闭');
  }

  async screenshot(outputPath) {
    const page = await this.getPage();
    return await page.screenshot({ path: outputPath, fullPage: true });
  }

  async evaluate(script, arg) {
    const page = await this.getPage();
    return await page.evaluate(script, arg);
  }
}

const instances = new Map();

function getBrowserManager(dataPath, options = {}) {
  if (!instances.has(dataPath)) {
    instances.set(dataPath, new BrowserManager(dataPath, options));
  }
  return instances.get(dataPath);
}

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
  getSystemBrowser,
  getSystemUserDataDir,
};
