---
name: login
description: |
  登录微博账号。

  当用户说以下任何内容时触发此 skill：
  - "登录微博"
  - "微博登录"
  - "扫码登录微博"
  - "weibo login"
  - 任何涉及登录微博的请求

  此 skill 自动完成：
  - 打开浏览器访问微博登录页
  - 显示二维码供用户扫描
  - 等待用户扫码完成
  - 保存登录 Cookie

  使用 Playwright 浏览器自动化。

compatibility: |
  - Node.js 18+
  - Playwright
  - 依赖：playwright
---

# 登录微博

## 工作流程

1. 启动浏览器（显示模式）
2. 打开微博登录页面
3. 切换到扫码登录
4. 显示二维码
5. 等待用户扫码
6. 登录成功后保存 Cookie
7. 关闭浏览器

## 输入参数

无

## 输出结果

```json
{
  "success": true,
  "userName": "用户名"
}
```

或

```json
{
  "success": false,
  "error": "错误信息"
}
```

## 使用示例

**示例 1：**
```
用户：登录微博
结果：打开浏览器，显示二维码
      请使用微博 APP 扫描二维码
      登录成功！用户名: xxx
```

## 依赖安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/weibo/login/scripts
npm install playwright
npx playwright install chromium
```

## 注意事项

1. 需要用户手动扫码
2. 二维码有效期约 2 分钟
3. 登录成功后会自动保存 Cookie
4. Cookie 文件保存在 `weibo/.cookies.json`
