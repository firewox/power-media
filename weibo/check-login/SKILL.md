---
name: weibo-check-login
description: |
  使用 computer-mcp 检查微博登录状态。
  
  当用户说以下任何内容时触发此 skill：
  - "检查微博登录状态"
  - "微博是否登录"
  - "查看微博登录"
  - "check weibo login"
  - "微博登录了吗"
  - 任何涉及检查微博登录状态的请求
  
  工作流程：
  1. 调用 computer-mcp/focus_window 聚焦微博窗口
  2. 调用 computer-mcp/inspect_screen 识别界面元素
  3. 分析 OCR 结果判断登录状态
  4. 返回登录状态和用户名
  
  依赖：
  - computer-mcp (focus_window, inspect_screen)
  - 已打开的微博浏览器窗口

compatibility:
  - computer-mcp >= 1.0
  - Windows 10/11
  - Edge / Chrome 浏览器
---

# 检查微博登录状态

## 工作流程（computer-mcp）

### Step 1: 聚焦微博窗口
```json
{
  "tool": "computer-mcp/focus_window",
  "params": {"title": "微博"}
}
```

### Step 2: 截图并识别界面
```json
{
  "tool": "computer-mcp/inspect_screen",
  "params": {}
}
```

### Step 3: 分析登录状态
从 OCR 结果中检查：
- **未登录**：检测到 "登录" / "注册" 按钮
- **已登录**：检测到用户名（如 "xxx 的微博"）或用户头像

## 输出结果

```json
{
  "loggedIn": true,
  "userName": "xxx"
}
```

或

```json
{
  "loggedIn": false,
  "userName": null
}
```

## 使用示例

**示例 1：**
```
用户：检查微博登录状态
AI：调用 computer-mcp 检查...
结果：已登录，用户名: xxx
```

**示例 2：**
```
用户：微博是否登录？
AI：调用 computer-mcp 检查...
结果：未登录，请先登录
```

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 找不到微博窗口 | 提示用户先打开浏览器访问 weibo.com |
| OCR 识别失败 | 重试截图，最多 3 次 |

## 注意事项

1. 必须先打开浏览器并访问 weibo.com
2. 确保微博窗口未被最小化
3. 窗口标题应包含 "微博" 以便 focus_window 识别
