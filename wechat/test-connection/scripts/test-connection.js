#!/usr/bin/env node
/**
 * 测试微信公众号 API 连接
 */

// 依赖检查
let axios;

try {
  axios = require('axios');
} catch (e) {
  console.error('缺少依赖包，请先安装：npm install axios');
  process.exit(1);
}

const WECHAT_API_BASE = 'https://api.weixin.qq.com';
const fs = require('fs');
const path = require('path');

// 加载配置（支持多种方式）
function loadConfig() {
  // 方式 1：环境变量（优先级最高）
  let appId = process.env.WECHAT_APP_ID;
  let appSecret = process.env.WECHAT_APP_SECRET;

  if (appId && appSecret) {
    console.log('✅ 已从环境变量加载配置');
    return { appId, appSecret, source: 'environment' };
  }

  // 方式 2：.env 文件
  const envPaths = [
    path.resolve(process.cwd(), '.env'),
    path.resolve(__dirname, '.env'),
    path.resolve(__dirname, '../.env'),
    path.resolve(__dirname, '../../.env')
  ];

  for (const envPath of envPaths) {
    if (fs.existsSync(envPath)) {
      const envContent = fs.readFileSync(envPath, 'utf-8');
      const envVars = {};
      envContent.split('\n').forEach(line => {
        const match = line.match(/^([^#=]+)=(.*)$/);
        if (match) {
          envVars[match[1].trim()] = match[2].trim().replace(/^["']|["']$/g, '');
        }
      });

      if (envVars.WECHAT_APP_ID && envVars.WECHAT_APP_SECRET) {
        console.log(`✅ 已从 .env 文件加载配置: ${envPath}`);
        return {
          appId: envVars.WECHAT_APP_ID,
          appSecret: envVars.WECHAT_APP_SECRET,
          source: 'env_file'
        };
      }
    }
  }

  // 方式 3：wechat-config.json 文件
  const configPaths = [
    path.resolve(process.cwd(), 'wechat-config.json'),
    path.resolve(__dirname, 'wechat-config.json'),
    path.resolve(__dirname, '../wechat-config.json'),
    path.resolve(__dirname, '../../wechat-config.json'),
    path.resolve(require('os').homedir(), '.wechat-config.json')
  ];

  for (const configPath of configPaths) {
    if (fs.existsSync(configPath)) {
      try {
        const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
        const wechatConfig = config.wechat || config;

        if (wechatConfig.appId && wechatConfig.appSecret) {
          console.log(`✅ 已从配置文件加载: ${configPath}`);
          return {
            appId: wechatConfig.appId,
            appSecret: wechatConfig.appSecret,
            source: 'config_file'
          };
        }
      } catch (e) {
        console.error(`⚠️  配置文件格式错误: ${configPath}`);
      }
    }
  }

  // 未找到配置
  throw new Error(
    '\n❌ 未找到微信公众号配置！\n\n' +
    '请使用以下任一方式配置：\n\n' +
    '【方式 1】环境变量（推荐）:\n' +
    '  export WECHAT_APP_ID="你的 AppID"\n' +
    '  export WECHAT_APP_SECRET="你的 AppSecret"\n\n' +
    '【方式 2】.env 文件:\n' +
    '  在项目根目录创建 .env 文件，内容如下：\n' +
    '  WECHAT_APP_ID=你的 AppID\n' +
    '  WECHAT_APP_SECRET=你的 AppSecret\n\n' +
    '【方式 3】wechat-config.json 文件:\n' +
    '  创建 wechat-config.json 文件，内容如下：\n' +
    '  {\n' +
    '    "appId": "你的 AppID",\n' +
    '    "appSecret": "你的 AppSecret"\n' +
    '  }\n\n' +
    '配置文件搜索路径（按优先级）：\n' +
    envPaths.concat(configPaths).map(p => `  - ${p}`).join('\n')
  );
}

// 主函数
async function testConnection() {
  const config = loadConfig();

  console.log('正在测试微信 API 连接...');
  console.log(`AppID: ${config.appId.substring(0, 6)}...`);

  try {
    const response = await axios.get(`${WECHAT_API_BASE}/cgi-bin/token`, {
      params: {
        grant_type: 'client_credential',
        appid: config.appId,
        secret: config.appSecret
      },
      timeout: 30000
    });

    if (response.data.access_token) {
      const { access_token, expires_in } = response.data;

      return {
        success: true,
        message: '微信 API 连接测试成功',
        appId: config.appId,
        accessToken: access_token,
        expiresIn: expires_in
      };
    }

    // 有错误返回
    const { errcode, errmsg } = response.data;
    let errorMessage = errmsg;

    // 常见错误处理
    switch (errcode) {
      case -1:
        errorMessage = '系统繁忙，请稍后再试';
        break;
      case 40001:
        errorMessage = 'AppSecret 错误或 AppID 无效';
        break;
      case 40002:
        errorMessage = '不合法的凭证类型';
        break;
      case 40013:
        errorMessage = 'AppID 无效';
        break;
      case 40125:
        errorMessage = 'AppSecret 无效';
        break;
      case 40164:
        errorMessage = '调用接口的 IP 地址不在白名单中';
        break;
    }

    throw new Error(`${errorMessage} (错误码: ${errcode})`);

  } catch (error) {
    if (error.message.includes('错误码')) {
      throw error;
    }
    if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND') {
      throw new Error('无法连接到微信服务器，请检查网络');
    }
    if (error.code === 'ETIMEDOUT') {
      throw new Error('连接超时，请检查网络或稍后重试');
    }
    throw new Error(`请求失败: ${error.message}`);
  }
}

// CLI
if (require.main === module) {
  testConnection()
    .then(result => {
      console.log('\n✅', result.message);
      console.log('='.repeat(50));
      console.log(`AppID: ${result.appId}`);
      console.log(`Access Token: ${result.accessToken.substring(0, 20)}...`);
      console.log(`有效期: ${result.expiresIn} 秒 (${Math.floor(result.expiresIn / 60)} 分钟)`);
      console.log('');
      console.log('配置检查通过！');
    })
    .catch(error => {
      console.error('\n❌ 连接测试失败');
      console.error('='.repeat(50));
      console.error('错误信息:', error.message);
      console.error('');
      console.error('可能的解决方案:');

      if (error.message.includes('AppSecret') || error.message.includes('AppID')) {
        console.error('  1. 检查 WECHAT_APP_ID 和 WECHAT_APP_SECRET 是否正确');
        console.error('  2. 确认使用的是什么类型的账号（公众号、小程序等）');
      }
      if (error.message.includes('IP') || error.message.includes('白名单')) {
        console.error('  1. 登录微信公众号后台');
        console.error('  2. 进入"开发" -> "基本配置" -> "IP白名单"');
        console.error('  3. 添加当前服务器的 IP 地址');
      }
      if (error.message.includes('环境变量')) {
        console.error('  1. 设置 WECHAT_APP_ID 环境变量');
        console.error('  2. 设置 WECHAT_APP_SECRET 环境变量');
      }
      if (error.message.includes('网络')) {
        console.error('  1. 检查网络连接');
        console.error('  2. 确认能够访问 https://api.weixin.qq.com');
      }

      process.exit(1);
    });
}

module.exports = { testConnection };
