---
name: rednote-like
description: |
  点赞/取消点赞小红书笔记。

  当用户说以下任何内容时触发此 skill：
  - "点赞小红书"
  - "给小红书点赞"
  - "取消点赞"
  - 任何涉及点赞小红书笔记的请求

  工作流程：
  1. 导航到笔记详情页
  2. 截图，多模态 AI 直接观察找到点赞按钮
  3. 点击点赞按钮
  4. 验证点赞状态

compatibility: |
  - computer-mcp >= 1.0
  - Windows 10/11
---

# 点赞/取消点赞

## 工作流程

### Step 1: 导航到笔记详情页

```python
note_url = f"https://www.xiaohongshu.com/explore/{noteId}"
automation.navigate_to(note_url)
```

### Step 2: 截图识别点赞按钮

```json
{"tool": "computer-mcp/inspect_screen", "params": {}}
```

AI 分析截图，找到点赞按钮（心形图标）的位置。

### Step 3: 点击点赞按钮

```json
{"tool": "computer-mcp/click", "params": {"x": detected_x, "y": detected_y}}
```

### Step 4: 验证结果

再次截图检查点赞状态（心形变红表示已点赞）。

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| noteId | string | 是 | 笔记ID |
| unlike | boolean | 否 | 是否取消点赞，默认 false |

## 输出结果

```json
{
  "success": true,
  "noteId": "笔记ID",
  "action": "like/unlike",
  "screenshot_path": "D:\\...\\rednote_like_xxx.png",
  "message": "请 AI 分析截图并指导点赞操作"
}
```
