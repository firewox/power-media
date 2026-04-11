---
name: weibo-post-text
description: |
  使用 computer-mcp 发布纯文本微博。
  
  当用户说以下任何内容时触发此 skill：
  - "发微博"
  - "发布微博"
  - "发送微博"
  - "发条微博"
  - "post weibo"
  - "发一条微博"
  - 任何涉及发布纯文本微博的请求
  
  工作流程：
  1. 调用 weibo-check-login 确认已登录
  2. 调用 computer-mcp/focus_window 聚焦微博窗口
  3. 调用 computer-mcp/inspect_screen 识别输入框
  4. 调用 computer-mcp/click 点击输入框
  5. 调用 computer-mcp/type_text 输入内容
  6. 调用 computer-mcp/inspect_screen 找到发送按钮
  7. 调用 computer-mcp/click 点击发送
  8. 调用 computer-mcp/confirm_action 确认发布
  9. 调用 computer-mcp/inspect_screen 验证发布成功
  
  依赖：
  - computer-mcp (focus_window, inspect_screen, click, type_text, confirm_action)
  - weibo-check-login skill
  - 已登录的微博浏览器窗口

compatibility:
  - computer-mcp >= 1.0
  - Windows 10/11
  - Edge / Chrome 浏览器
---

# 发布纯文本微博

## 工作流程（computer-mcp）

### Step 1: 检查登录状态
先调用 `weibo-check-login` 确认已登录。

### Step 2: 聚焦微博窗口
```json
{
  "tool": "computer-mcp/focus_window",
  "params": {"title": "微博"}
}
```

### Step 3: 识别输入框
```json
{
  "tool": "computer-mcp/inspect_screen",
  "params": {}
}
```

从 OCR 结果中定位 "有什么新鲜事想告诉大家" 的坐标。

### Step 4: 点击输入框
```json
{
  "tool": "computer-mcp/click",
  "params": {"x": <detected_x>, "y": <detected_y>}
}
```

### Step 5: 输入内容
```json
{
  "tool": "computer-mcp/type_text",
  "params": {"text": "{{content}}"}
}
```

### Step 6: 找到并点击发送按钮
```json
{
  "tool": "computer-mcp/inspect_screen",
  "params": {}
}
```

从 OCR 结果中找到 "发送" 按钮坐标并点击：
```json
{
  "tool": "computer-mcp/click",
  "params": {"x": <send_button_x>, "y": <send_button_y>}
}
```

### Step 7: 确认发布
```json
{
  "tool": "computer-mcp/confirm_action",
  "params": {"action_description": "确认发布微博？"}
}
```

### Step 8: 验证结果
再次调用 `inspect_screen` 检查是否有 "发布成功" 提示。

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| text | string | 是 | 微博内容，最多 140 字符 |

## 输出结果

```json
{
  "success": true,
  "message": "发布成功",
  "url": "https://weibo.com/xxx/xxx"
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
AI：
  1. 检查登录状态 ✓
  2. 聚焦微博窗口
  3. 点击输入框
  4. 输入内容
  5. 点击发送
  6. 确认发布
结果：发布成功！
```

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 未登录 | 返回错误，提示先执行 weibo-login |
| 找不到输入框 | 重试截图，或提示用户检查页面 |
| 内容超长 | Skill 层校验，拒绝执行（>140字符） |
| 发送失败 | 返回错误信息 |

## 注意事项

1. 必须先打开浏览器并访问 weibo.com
2. 确保微博窗口未被最小化
3. 内容长度限制 140 字符
4. 高风险操作需人工确认
