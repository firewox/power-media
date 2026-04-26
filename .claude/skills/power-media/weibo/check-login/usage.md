# check-login

检查微博登录状态。

## 功能

- 检查当前是否已登录微博
- 显示登录用户名
- 自动使用保存的 Cookie

## 安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/weibo/check-login/scripts
npm install playwright
npx playwright install chromium
```

## 使用方法

### CLI 使用

```bash
node scripts/check-login.js
```

### 输出示例

**已登录：**
```
正在检查微博登录状态...
已登录
用户名: 张三
```

**未登录：**
```
正在检查微博登录状态...
未登录
请先运行 login skill 进行登录
```

## 工作流程

1. 启动浏览器（无界面模式）
2. 加载已保存的 Cookie
3. 访问 https://weibo.com
4. 检查页面上的用户元素
5. 返回登录状态和用户名

## Cookie 存储

Cookie 文件保存在 `weibo/.cookies.json`

如果删除此文件，需要重新登录。
