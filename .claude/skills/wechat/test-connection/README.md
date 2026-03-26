# test-connection

测试微信公众号 API 连接。

## 功能

- 获取 access_token
- 验证配置是否正确
- 检查网络连接和 API 可用性

## 安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/.claude/skills/wechat/test-connection/scripts
chmod +x install-deps.sh
./install-deps.sh
```

或手动安装：

```bash
npm install axios
```

## 配置

设置环境变量：

```bash
export WECHAT_APP_ID="你的 AppID"
export WECHAT_APP_SECRET="你的 AppSecret"
```

## 使用方法

### 作为模块使用

```javascript
const { testConnection } = require('./scripts/test-connection');

const result = await testConnection();
console.log(result.message);
if (result.success) {
  console.log('Access Token:', result.accessToken);
}
```

### CLI 使用

```bash
node scripts/test-connection.js
```

## API

### testConnection()

测试微信 API 连接。

**返回值：**

```javascript
{
  success: true,           // 是否成功
  message: '...',          // 结果消息
  appId: 'wx...',          // AppID
  accessToken: 'xxx...',   // Access Token（成功时返回）
  expiresIn: 7200          // Token 有效期（秒）
}
```

## 常见错误

1. **invalid appid**: AppID 错误
2. **invalid appsecret**: AppSecret 错误
3. **ip not in whitelist**: 服务器 IP 未在白名单中
