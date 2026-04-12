---
name: rednote-comment
description: |
  发表评论。

  当用户说以下任何内容时触发此 skill：
  - "评论小红书"
  - "给小红书写评论"
  - "发表评论"
  - 任何涉及评论小红书笔记的请求

  工作流程：
  1. 导航到笔记详情页
  2. 找到评论输入框
  3. 输入评论内容
  4. 点击发送
  5. 确认操作

compatibility: |
  - computer-mcp >= 1.0
  - Windows 10/11
---

# 发表评论

## 工作流程

### Step 1: 导航到笔记详情页

```python
note_url = f"https://www.xiaohongshu.com/explore/{noteId}"
automation.navigate_to(note_url)
```

### Step 2: 找到评论输入框

```json
{"tool": "computer-mcp/inspect_screen", "params": {}}
```

AI 分析截图，找到评论输入框（"说点什么..."）。

### Step 3: 输入评论内容

```json
{"tool": "computer-mcp/click", "params": {"x": input_x, "y": input_y}}
{"tool": "computer-mcp/type_text", "params": {"text": "评论内容"}}
```

### Step 4: 点击发送

找到"发送"按钮并点击。

### Step 5: 确认操作

```json
{"tool": "computer-mcp/confirm_action", "params": {"action_description": "确认发表评论？"}}
```

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| noteId | string | 是 | 笔记ID |
| content | string | 是 | 评论内容 |

## 输出结果

```json
{
  "success": true,
  "noteId": "笔记ID",
  "content": "评论内容",
  "screenshot_path": "D:\\...\\rednote_comment_xxx.png",
  "message": "请 AI 分析截图并指导评论操作"
}
```

## 注意事项

1. 评论内容需符合社区规范
2. 敏感操作需人工确认
