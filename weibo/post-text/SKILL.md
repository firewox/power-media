---
name: post-text
description: |
  使用浏览器自动化发布纯文本微博。

  当用户说以下任何内容时触发此 skill：
  - "发微博"
  - "发布微博"
  - "发送微博"
  - "发条微博"
  - "post weibo"
  - 任何涉及发布纯文本微博的请求

  此 skill 自动完成：
  - 检查登录状态
  - 打开微博首页
  - 填写微博内容
  - 点击发送按钮
  - 返回发布结果

  使用 Playwright 浏览器自动化。

compatibility: |
  - Node.js 18+
  - Playwright
  - 已登录的微博账号
  - 依赖：playwright
---

# 发布纯文本微博

## 工作流程

1. 检查登录状态
2. 启动浏览器
3. 打开微博首页
4. 填写微博内容
5. 点击发送
6. 检查发布结果
7. 返回结果

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| text | string | 是 | 微博内容（最多 140 字符）|

## 输出结果

```json
{
  "success": true,
  "message": "发布成功"
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
用户：发条微博说"今天天气真好"
结果：正在发布微博...
      发布成功！
```

## 依赖安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/weibo/post-text/scripts
npm install playwright
npx playwright install chromium
```

## 注意事项

1. 必须先登录微博
2. 内容最多 140 字符
3. 使用 headless 模式（不显示浏览器）
