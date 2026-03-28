const { chromium } = require('playwright');
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

async function findChromeDebuggerPort() {
  try {
    if (process.platform === 'win32') {
      const { stdout } = await execPromise(
        'wmic process where "name=\'msedge.exe\' or name=\'chrome.exe\'" get CommandLine /format:list'
      );
      
      const lines = stdout.split('\n');
      for (const line of lines) {
        if (line.includes('--remote-debugging-port=')) {
          const match = line.match(/--remote-debugging-port=(\d+)/);
          if (match) {
            return parseInt(match[1], 10);
          }
        }
      }
    } else {
      const { stdout } = await execPromise('ps aux | grep -E "(chrome|edge)" | grep remote-debugging');
      const match = stdout.match(/--remote-debugging-port=(\d+)/);
      if (match) {
        return parseInt(match[1], 10);
      }
    }
  } catch (e) {
    // No browser with debugging port found
  }
  return null;
}

async function connectToExistingBrowser(port) {
  try {
    const browser = await chromium.connectOverCDP(`http://localhost:${port}`);
    return browser;
  } catch (e) {
    throw new Error(`无法连接到浏览器: ${e.message}`);
  }
}

module.exports = {
  findChromeDebuggerPort,
  connectToExistingBrowser,
};
