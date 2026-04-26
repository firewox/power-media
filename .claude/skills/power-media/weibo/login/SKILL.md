---
name: weibo-login
description: |
  使用 computer-mcp 完成微博扫码登录。
  
  当用户说以下任何内容时触发此 skill：
  - "登录微博"
  - "微博登录"
  - "扫码登录微博"
  - "weibo login"
  - "微博扫码登录"
  - 任何涉及登录微博的请求
  
  工作流程：
  1. 调用 computer-mcp/focus_window 聚焦浏览器窗口
  2. 调用 computer-mcp 键盘快捷键访问 weibo.com
  3. 调用 computer-mcp/inspect_screen 找到扫码登录入口
  4. 调用 computer-mcp/click 切换到扫码登录
  5. 等待用户扫码完成
  6. 调用 computer-mcp/inspect_screen 验证登录成功
  
  依赖：
  - computer-mcp (focus_window, inspect_screen, click, type_text, hotkey, press_key, wait)
  - Edge / Chrome 浏览器

compatibility:
  - computer-mcp >= 1.0
  - Windows 10/11
  - Edge / Chrome 浏览器
---

# 微博扫码登录

## 工作流程（computer-mcp）

### Step 1: 聚焦浏览器窗口
```json
{
  "tool": "computer-mcp/focus_window",
  "params": {"title": "Edge"}
}
```

### Step 2: 访问微博登录页
```json
{
  "tool": "computer-mcp/hotkey",
  "params": {"keys": ["ctrl", "l"]}
}
```

```json
{
  "tool": "computer-mcp/type_text",
  "params": {"text": "weibo.com"}
}
```

```json
{
  "tool": "computer-mcp/press_key",
  "params": {"key": "enter"}
}
```

### Step 3: 切换到扫码登录
```json
{
  "tool": "computer-mcp/inspect_screen",
  "params": {}
}
```

从 OCR 结果中找到 "扫码登录" 坐标并点击：
```json
{
  "tool": "computer-mcp/click",
  "params": {"x": <detected_x>, "y": <detected_y>}
}
```

### Step 4: 等待用户扫码
显示二维码，提示用户使用手机微博 APP 扫码。

```json
{
  "tool": "computer-mcp/wait",
  "params": {"seconds": 3}
}
```

### Step 5: 验证登录成功
循环检查登录状态（最多 2 分钟）：
```json
{
  "tool": "computer-mcp/inspect_screen",
  "params": {}
}
```

检测到用户名即表示登录成功。

## 输出结果

```json
{
  "success": true,
  "userName": "xxx",
  "message": "登录成功"
}
```

或

```json
{
  "success": false,
  "error": "登录超时或用户取消"
}
```

## 使用示例

**示例 1：**
```
用户：登录微博
AI：
  1. 聚焦浏览器窗口
  2. 访问 weibo.com
  3. 切换到扫码登录
  4. 等待用户扫码...
  
  请使用手机微博 APP 扫描二维码
  
结果：登录成功！用户名: xxx
```

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 找不到浏览器窗口 | 提示用户打开 Edge/Chrome |
| 二维码超时 | 提示刷新页面重试 |
| 用户取消登录 | 返回取消状态 |

## 注意事项

1. 二维码有效期约 2 分钟
2. 需使用手机微博 APP 扫码
3. 登录会话保存在浏览器中
4. 下次访问自动保持登录状态
