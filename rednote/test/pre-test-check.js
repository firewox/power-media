#!/usr/bin/env node
/**
 * 测试前环境检查脚本
 * 
 * 运行所有测试前，先执行此脚本检查环境
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const CHECKS = {
  // 检查 Playwright 安装
  playwright: () => {
    try {
      const result = execSync('npm list playwright --depth=0', { encoding: 'utf8' });
      const version = result.match(/playwright@(\d+\.\d+\.\d+)/);
      return {
        success: true,
        message: `Playwright ${version ? version[1] : '已安装'}`
      };
    } catch (e) {
      return {
        success: false,
        message: 'Playwright 未安装',
        fix: 'npm install playwright'
      };
    }
  },

  // 检查浏览器安装
  browser: () => {
    const os = process.platform;
    let browserPath;
    
    if (os === 'win32') {
      browserPath = path.join(
        process.env.LOCALAPPDATA || '',
        'ms-playwright',
        'firefox-1509',
        'firefox',
        'firefox.exe'
      );
    } else if (os === 'darwin') {
      browserPath = path.join(
        process.env.HOME || '',
        'Library',
        'Caches',
        'ms-playwright',
        'firefox-1509',
        'firefox',
        'Nightly.app'
      );
    } else {
      browserPath = path.join(
        process.env.HOME || '',
        '.cache',
        'ms-playwright',
        'firefox-1509',
        'firefox',
        'firefox'
      );
    }

    if (fs.existsSync(browserPath)) {
      return {
        success: true,
        message: `Firefox 浏览器已安装 (${browserPath})`
      };
    }

    return {
      success: false,
      message: 'Firefox 浏览器未安装',
      fix: 'npx playwright install firefox'
    };
  },

  // 检查数据目录
  dataDir: () => {
    const dataPath = path.join(__dirname, '..', 'data');
    if (!fs.existsSync(dataPath)) {
      fs.mkdirSync(dataPath, { recursive: true });
      return {
        success: true,
        message: '已创建 data/ 目录'
      };
    }
    return {
      success: true,
      message: 'data/ 目录已存在'
    };
  },

  // 检查 debug 目录
  debugDir: () => {
    const debugPath = path.join(__dirname, '..', 'debug');
    if (!fs.existsSync(debugPath)) {
      fs.mkdirSync(debugPath, { recursive: true });
      return {
        success: true,
        message: '已创建 debug/ 目录（用于截图）'
      };
    }
    return {
      success: true,
      message: 'debug/ 目录已存在'
    };
  },

  // 检查 lib 模块
  libModules: () => {
    const libPath = path.join(__dirname, '..', 'lib');
    const required = ['browser.js', 'cookie.js', 'utils.js'];
    const missing = [];

    for (const file of required) {
      if (!fs.existsSync(path.join(libPath, file))) {
        missing.push(file);
      }
    }

    if (missing.length > 0) {
      return {
        success: false,
        message: `缺少 lib 模块: ${missing.join(', ')}`
      };
    }

    return {
      success: true,
      message: '所有 lib 模块已就绪'
    };
  },

  // 检查测试图片
  testImages: () => {
    const testDataPath = path.join(__dirname, '..', 'test-data');
    if (!fs.existsSync(testDataPath)) {
      fs.mkdirSync(testDataPath, { recursive: true });
      return {
        success: true,
        warning: true,
        message: '已创建 test-data/ 目录（请添加测试图片）'
      };
    }

    const files = fs.readdirSync(testDataPath);
    const images = files.filter(f => /\.(jpg|jpeg|png)$/i.test(f));

    if (images.length === 0) {
      return {
        success: true,
        warning: true,
        message: 'test-data/ 中没有图片（publish-note 测试需要）'
      };
    }

    return {
      success: true,
      message: `找到 ${images.length} 张测试图片`
    };
  }
};

async function runChecks() {
  console.log('🔍 RedNote Skills 测试前检查\n');
  console.log('=' .repeat(60));

  const results = [];
  let hasErrors = false;
  let hasWarnings = false;

  for (const [name, checkFn] of Object.entries(CHECKS)) {
    process.stdout.write(`检查 ${name}... `);
    
    try {
      const result = checkFn();
      results.push({ name, ...result });

      if (result.success && !result.warning) {
        console.log('✅');
        console.log(`   ${result.message}`);
      } else if (result.success && result.warning) {
        console.log('⚠️');
        console.log(`   ${result.message}`);
        hasWarnings = true;
      } else {
        console.log('❌');
        console.log(`   ${result.message}`);
        if (result.fix) {
          console.log(`   修复: ${result.fix}`);
        }
        hasErrors = true;
      }
    } catch (e) {
      console.log('❌');
      console.log(`   检查失败: ${e.message}`);
      hasErrors = true;
    }
    
    console.log();
  }

  console.log('=' .repeat(60));

  if (hasErrors) {
    console.log('\n❌ 检查未通过，请先修复以上问题');
    console.log('\n建议命令:');
    console.log('  npm install playwright');
    console.log('  npx playwright install firefox');
    process.exit(1);
  } else if (hasWarnings) {
    console.log('\n⚠️ 检查通过，但有警告（非阻塞）');
    process.exit(0);
  } else {
    console.log('\n✅ 所有检查通过，可以开始测试');
    console.log('\n建议测试顺序:');
    console.log('  1. node get-feeds/scripts/get-feeds.js --count 5');
    console.log('  2. node check-login/scripts/check-login.js');
    console.log('  3. node get-qrcode/scripts/get-qrcode.js');
    process.exit(0);
  }
}

runChecks();
