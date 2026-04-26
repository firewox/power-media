---
name: weibo-post-with-image
description: |
  使用 computer-mcp 发布带图片的微博。
  
  当用户说以下任何内容时触发此 skill：
  - "发带图微博"
  - "发布带图片的微博"
  - "发微博带图"
  - "发图片微博"
  - "post weibo with image"
  - "发微博带图片"
  - 任何涉及发布带图片的微博的请求
  
  工作流程：
  1. 调用 weibo-check-login 确认已登录
  2. 调用 computer-mcp/focus_window 聚焦微博窗口
  3. 调用 computer-mcp/inspect_screen 识别输入框
  4. 调用 computer-mcp/click 点击输入框
  5. 调用 computer-mcp/type_text 输入内容
  6. 调用 computer-mcp/inspect_screen 找到图片按钮
  7. 调用 computer-mcp/click 点击添加图片
  8. 调用 computer-mcp/type_text 输入图片路径
  9. 调用 computer-mcp/wait 等待上传完成
  10. 调用 computer-mcp/click 点击发送
  11. 调用 computer-mcp/confirm_action 确认发布
  12. 调用 computer-mcp/inspect_screen 验证发布成功
  
  依赖：
  - computer-mcp (focus_window, inspect_screen, click, type_text, confirm_action, wait, press_key)
  - weibo-check-login skill
  - 已登录的微博浏览器窗口

compatibility:
  - computer-mcp >= 1.0
  - Windows 10/11
  - Edge / Chrome 浏览器
---

# 发布带图片的微博

## 工作流程（computer-mcp）

### Step 1: 前置检查
调用 `weibo-check-login` 确认已登录，并校验图片文件存在。

### Step 2: 聚焦微博窗口
```json
{
  "tool": "computer-mcp/focus_window",
  "params": {"title": "微博"}
}
```

### Step 3: 点击输入框
```json
{
  "tool": "computer-mcp/inspect_screen",
  "params": {}
}
```

找到 "有什么新鲜事想告诉大家" 并点击：
```json
{
  "tool": "computer-mcp/click",
  "params": {"x": <input_x>, "y": <input_y>}
}
```

### Step 4: 输入文字
```json
{
  "tool": "computer-mcp/type_text",
  "params": {"text": "{{content}}"}
}
```

### Step 5: 点击添加图片
```json
{
  "tool": "computer-mcp/inspect_screen",
  "params": {}
}
```

找到 "图片" 图标并点击：
```json
{
  "tool": "computer-mcp/click",
  "params": {"x": <image_button_x>, "y": <image_button_y>}
}
```

### Step 6: 选择图片文件
在文件选择对话框中输入图片路径：
```json
{
  "tool": "computer-mcp/type_text",
  "params": {"text": "{{image_path}}"}
}
```

```json
{
  "tool": "computer-mcp/press_key",
  "params": {"key": "enter"}
}
```

### Step 7: 等待上传
```json
{
  "tool": "computer-mcp/wait",
  "params": {"seconds": 3}
}
```

循环检查上传进度（通过 inspect_screen 看是否有缩略图）。

### Step 8: 点击发送
找到 "发送" 按钮并点击：
```json
{
  "tool": "computer-mcp/click",
  "params": {"x": <send_x>, "y": <send_y>}
}
```

### Step 9: 确认发布
```json
{
  "tool": "computer-mcp/confirm_action",
  "params": {"action_description": "确认发布带图微博？"}
}
```

### Step 10: 验证结果
检查 "发布成功" 提示。

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| text | string | 否 | 微博内容，最多 140 字符 |
| image_path | string | 是 | 图片文件路径，支持 JPG/PNG/GIF |

## 图片要求

- 格式：JPG, PNG, GIF
- 大小：建议 ≤ 5MB
- 数量：本 skill 支持 1-9 张

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
用户：发一条带图片的微博，说"分享美景"，图片 C:\Photos\scenic.jpg
AI：
  1. 检查登录状态 ✓
  2. 聚焦微博窗口
  3. 点击输入框，输入文字
  4. 点击添加图片按钮
  5. 选择图片文件
  6. 等待上传
  7. 点击发送
  8. 确认发布
结果：发布成功！
```

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 图片不存在 | 返回错误，提示检查路径 |
| 上传失败 | 重试或返回错误 |
| 格式不支持 | 提示支持的格式（JPG/PNG/GIF） |

## 注意事项

1. 图片路径需使用绝对路径或相对于工作目录的路径
2. 上传大图片可能需要更长时间
3. 最多支持 9 张图片
4. 上传过程中请勿操作浏览器
