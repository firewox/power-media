# check-login

检查小红书账号登录状态。

## 功能

- 启动浏览器并加载已保存的 Cookie
- 访问小红书创作者中心检测登录状态
- 返回登录状态和用户信息

## 安装依赖

```bash
cd rednote/check-login/scripts
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
const { checkLogin } = require('./scripts/check-login');

const result = await checkLogin();
console.log(result);

// 输出:
// {
//   success: true,
//   isLoggedIn: true,
//   username: "用户昵称",
//   userId: "用户ID"
// }
```

### CLI 使用

```bash
node scripts/check-login.js
```

## 输出

**已登录：**
```json
{
  "success": true,
  "isLoggedIn": true,
  "username": "用户昵称",
  "userId": "用户ID",
  "message": "已登录"
}
```

**未登录：**
```json
{
  "success": true,
  "isLoggedIn": false,
  "message": "未登录，请先执行 get-qrcode 获取登录二维码"
}
```

## 相关 Skills

- `get-qrcode` - 获取登录二维码
- `logout` - 登出/清除登录状态
