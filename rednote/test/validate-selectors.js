#!/usr/bin/env node
/**
 * 选择器验证工具
 * 
 * 验证 CSS 选择器是否匹配当前页面结构
 * 当选择器失效时，帮助找到新的正确选择器
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const DEFAULT_SELECTORS = {
  'login-qrcode': [
    '.qrcode-box img',
    '.login-qrcode img',
    '[class*="qr"] img',
    'canvas',
    '.qrcode img'
  ],
  'user-info': [
    '.user-info',
    '.user-name',
    '.avatar',
    '[class*="user"]'
  ],
  'login-button': [
    '.login-btn',
    'button:has-text("登录")',
    '[class*="login"]'
  ],
  'search-input': [
    'input[placeholder*="搜索"]',
    '.search-input',
    'input[type="search"]'
  ],
  'feed-item': [
    '.note-item',
    '[class*="feed"]',
    '[class*="note"]'
  ]
};

async function validateSelectors(url, customSelectors = {}) {
  const selectors = { ...DEFAULT_SELECTORS, ...customSelectors };
  
  console.log(`\n🔍 验证选择器: ${url}\n`);
  console.log('='.repeat(70));
  
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(3000);
    
    const results = {};
    
    for (const [name, selectorList] of Object.entries(selectors)) {
      console.log(`\n📌 ${name}:`);
      
      let found = false;
      for (const selector of selectorList) {
        try {
          const element = await page.$(selector);
          if (element) {
            const count = await page.$$eval(selector, els => els.length);
            console.log(`  ✅ ${selector} (${count}个元素)`);
            results[name] = selector;
            found = true;
            break;
          } else {
            console.log(`  ❌ ${selector}`);
          }
        } catch (e) {
          console.log(`  ❌ ${selector} (${e.message})`);
        }
      }
      
      if (!found) {
        console.log(`  ⚠️ 未找到有效选择器`);
        results[name] = null;
      }
    }
    
    console.log('\n' + '='.repeat(70));
    console.log('\n📊 验证结果:');
    
    const valid = Object.entries(results).filter(([_, v]) => v !== null);
    const invalid = Object.entries(results).filter(([_, v]) => v === null);
    
    console.log(`  ✅ 有效: ${valid.length}/${Object.keys(results).length}`);
    
    if (invalid.length > 0) {
      console.log(`\n  ❌ 需要修复的选择器:`);
      invalid.forEach(([name]) => {
        console.log(`    - ${name}`);
      });
    }
    
    // 保存截图
    const screenshotPath = path.join(
      __dirname, 
      '..', 
      'debug', 
      `validate-${Date.now()}.png`
    );
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`\n📸 截图已保存: ${screenshotPath}`);
    
    // 提取页面所有 class（用于发现新选择器）
    console.log('\n🔍 页面 Class 样例（前20个）:');
    const classes = await page.evaluate(() => {
      const allClasses = [];
      document.querySelectorAll('*').forEach(el => {
        if (el.className && typeof el.className === 'string') {
          allClasses.push(...el.className.split(' '));
        }
      });
      return [...new Set(allClasses)].filter(c => c.length > 3).slice(0, 20);
    });
    
    classes.forEach(c => console.log(`  .${c}`));
    
    return results;
    
  } catch (error) {
    console.error('验证失败:', error.message);
    throw error;
  } finally {
    await browser.close();
  }
}

async function main() {
  const args = process.argv.slice(2);
  const urlIndex = args.indexOf('--url');
  
  if (urlIndex === -1 || !args[urlIndex + 1]) {
    console.log('用法: node validate-selectors.js --url <网页URL>');
    console.log('');
    console.log('示例:');
    console.log('  node validate-selectors.js --url "https://creator.xiaohongshu.com/"');
    console.log('  node validate-selectors.js --url "https://www.xiaohongshu.com/"');
    process.exit(1);
  }
  
  const url = args[urlIndex + 1];
  
  try {
    await validateSelectors(url);
    process.exit(0);
  } catch (error) {
    console.error('验证失败:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { validateSelectors };
