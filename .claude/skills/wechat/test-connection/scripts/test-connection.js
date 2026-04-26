#!/usr/bin/env node
/**
 * 测试微信公众号 API 连接
 */
const axios = require('axios');
const {
  AccessTokenManager,
  exitWithError,
  hasJsonFlag,
  loadConfig,
  printResult
} = require('../../lib/wechat-common');

async function testConnection() {
  const config = loadConfig();
  const tokenManager = new AccessTokenManager(axios, config.appId, config.appSecret);
  const accessToken = await tokenManager.getAccessToken();

  return {
    success: true,
    stage: 'test-connection',
    message: '微信 API 连接测试成功',
    app_id: config.appId,
    config_source: config.source,
    access_token_preview: `${accessToken.substring(0, 12)}...`
  };
}

if (require.main === module) {
  const args = process.argv.slice(2);
  const asJson = hasJsonFlag(args);

  testConnection()
    .then(result => {
      if (asJson) {
        printResult(result, true);
        return;
      }
      console.log('\n✅', result.message);
      console.log(`AppID: ${result.app_id}`);
      console.log(`配置来源: ${result.config_source}`);
      console.log(`Access Token: ${result.access_token_preview}`);
    })
    .catch(error => exitWithError(error, asJson));
}

module.exports = { testConnection };
