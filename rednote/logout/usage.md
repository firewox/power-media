# logout

登出小红书账号并清除本地登录数据。

## 功能

- 清除本地保存的 Cookie
- 清除浏览器数据目录
- 清除登录状态缓存

## 安装依赖

无外部依赖。

## 配置

设置环境变量（可选）：

```bash
export XHS_DATA_PATH="/path/to/data"
```

## 使用方法

### 作为模块使用

```javascript
const { logout } = require('./scripts/logout');

const result = await logout();
console.log(result);
// { success: true, message: '已清除所有登录数据' }
```

### CLI 使用

```bash
node scripts/logout.js
```

## 输出

```json
{
  "success": true,
  "message": "已清除所有登录数据"
}
```

## 相关 Skills

- `get-qrcode` - 获取登录二维码
- `check-login` - 检查登录状态
