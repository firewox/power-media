# get-qrcode

获取小红书登录二维码，支持扫码登录并自动保存 Cookie。

## 功能

- 启动浏览器访问小红书登录页
- 获取并显示登录二维码
- 等待用户扫码登录
- 登录成功后自动保存 Cookie

## 安装依赖

```bash
cd rednote/get-qrcode/scripts
npm install playwright
```

## 配置

设置环境变量（可选）：

```bash
export XHS_DATA_PATH="/path/to/data"
```

## 使用方法

### 作为模块使用

```javascript
const { getQrcode, waitForLogin } = require('./scripts/get-qrcode');

// 仅获取二维码
const result = await getQrcode();
console.log(result.qrcodePath);

// 获取二维码并等待登录
const loginResult = await waitForLogin();
console.log(loginResult.isLoggedIn);
```

### CLI 使用

```bash
# 获取二维码并等待登录
node scripts/get-qrcode.js

# 仅获取二维码
node scripts/get-qrcode.js --no-wait
```

## 输出

**二维码生成：**
```json
{
  "success": true,
  "qrcodePath": "/path/to/qrcode.png",
  "message": "请扫描二维码登录"
}
```

**登录成功：**
```json
{
  "success": true,
  "isLoggedIn": true,
  "username": "用户昵称",
  "userId": "用户ID"
}
```

## 相关 Skills

- `check-login` - 检查登录状态
- `logout` - 登出/清除登录状态
