---
name: check-login
description: |
  检查微博登录状态。

  当用户说以下任何内容时触发此 skill：
  - "检查微博登录状态"
  - "微博是否登录"
  - "查看微博登录"
  - "check weibo login"
  - 任何涉及检查微博登录状态的请求

  此 skill 返回：
  - 登录状态（已登录/未登录）
  - 如果已登录，显示用户名

  使用 Playwright 浏览器自动化检查。

compatibility: |
  - Node.js 18+
  - Playwright
  - 依赖：playwright
---

# 检查微博登录状态

## 工作流程

1. 启动浏览器（headless 模式）
2. 加载已保存的 Cookie
3. 访问微博首页
4. 检查页面元素判断登录状态
5. 返回结果

## 输入参数

无

## 输出结果

```json
{
  "loggedIn": true,
  "userName": "用户名"
}
```

或

```json
{
  "loggedIn": false
}
```

## 使用示例

**示例 1：**
```
用户：检查微博登录状态
结果：已登录，用户名: xxx
```

**示例 2：**
```
用户：微博是否登录？
结果：未登录，请先登录
```

## 依赖安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/weibo/check-login/scripts
npm install playwright
npx playwright install chromium
```

## 注意事项

1. 会自动加载之前保存的 Cookie
2. 如果 Cookie 过期，会返回未登录状态
3. 需要配合 login skill 使用
