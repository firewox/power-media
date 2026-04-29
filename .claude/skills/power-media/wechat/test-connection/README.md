# test-connection

测试微信公众号 API 连接。

## 功能

- 获取 access_token
- 验证配置是否正确
- 检查网络连接和 API 可用性

## 安装

```powershell
powershell -ExecutionPolicy Bypass -File D:\08_tmp\02_media\power-media\.claude\skills\wechat\install-deps.ps1
```

## 配置

支持三种配置方式：

### 方式 1：环境变量
```powershell
$env:WECHAT_APP_ID="你的 AppID"
$env:WECHAT_APP_SECRET="你的 AppSecret"
```

### 方式 2：.env 文件
创建 `.env` 文件：
```
WECHAT_APP_ID=你的 AppID
WECHAT_APP_SECRET=你的 AppSecret
```

### 方式 3：JSON 配置文件
创建 `wechat-config.json`：
```json
{
  "WECHAT_APP_ID": "你的 AppID",
  "WECHAT_APP_SECRET": "你的 AppSecret"
}
```

## 使用方法

### 作为模块使用

```javascript
const { testConnection } = require('./scripts/test-connection');

const result = await testConnection();
console.log(result.message);
if (result.success) {
  console.log('App ID:', result.app_id);
}
```

### CLI 使用

```powershell
node scripts/test-connection.js
node scripts/test-connection.js --json
```

## API

### testConnection()

测试微信 API 连接。

**返回值：**

```javascript
{
  success: true,
  stage: 'test-connection',
  message: '...',
  app_id: 'wx...',
  config_source: 'environment',
  access_token_preview: 'xxx...'
}
```

## 常见错误

1. **invalid appid**: AppID 错误
2. **invalid appsecret**: AppSecret 错误
3. **ip not in whitelist**: 服务器 IP 未在白名单中
