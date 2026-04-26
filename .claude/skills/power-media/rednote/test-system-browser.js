const { SystemBrowserManager } = require('./lib/system-browser');

async function testCheckLogin() {
  console.log('🧪 测试 check-login with 系统浏览器');
  console.log('='.repeat(60));
  
  try {
    const browserManager = new SystemBrowserManager({
      headless: false,
      width: 1280,
      height: 720,
    });
    
    await browserManager.launch();
    
    const page = await browserManager.getPage();
    
    console.log('\n📱 访问小红书创作者中心...');
    await page.goto('https://creator.xiaohongshu.com/', { 
      waitUntil: 'domcontentloaded',
      timeout: 60000 
    });
    
    console.log('⏳ 等待页面加载...');
    await page.waitForTimeout(5000);
    
    const currentUrl = page.url();
    console.log(`\n📍 当前URL: ${currentUrl}`);
    
    const selectors = [
      '.user-info', 
      '.user-name', 
      '.avatar',
      '[class*="user"]',
      '.login-btn',
      'button:has-text("登录")',
      '.qrcode-box',
      '[class*="qr"]'
    ];
    
    console.log('\n🔍 检测页面元素...');
    for (const selector of selectors) {
      try {
        const element = await page.$(selector);
        if (element) {
          const text = await element.textContent().catch(() => '');
          console.log(`  ✅ ${selector}: ${text.slice(0, 30)}`);
        }
      } catch (e) {
        // Element not found
      }
    }
    
    let username = null;
    try {
      username = await page.$eval('.user-name, .nickname, [class*="user-name"]', el => el.textContent);
      if (username) {
        username = username.trim();
      }
    } catch (e) {
      // Not found
    }
    
    console.log('\n' + '='.repeat(60));
    if (username) {
      console.log(`✅ 已登录!`);
      console.log(`👤 用户名: ${username}`);
    } else if (!currentUrl.includes('login')) {
      console.log('✅ 看起来已登录 (不在登录页)');
    } else {
      console.log('❌ 未登录 - 在登录页面');
    }
    console.log('='.repeat(60));
    
    console.log('\n⏳ 15秒后关闭浏览器...');
    await page.waitForTimeout(15000);
    
    await browserManager.close();
    console.log('\n✅ 测试完成');
    
  } catch (error) {
    console.error('\n❌ 测试失败:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

testCheckLogin();
