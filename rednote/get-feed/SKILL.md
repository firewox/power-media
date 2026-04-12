---
name: rednote-get-feed
description: |
  获取帖子详情。

  当用户说以下任何内容时触发此 skill：
  - "获取笔记详情"
  - "查看小红书笔记"
  - "获取帖子详情"
  - 任何涉及获取小红书帖子详情的请求

  工作流程：
  1. 导航到笔记详情页
  2. 截图识别页面内容
  3. AI 提取笔记信息

compatibility: |
  - computer-mcp >= 1.0
  - Windows 10/11
---

# 获取帖子详情

## 工作流程

### Step 1: 导航到笔记详情页

```python
note_url = f"https://www.xiaohongshu.com/explore/{noteId}"
automation.navigate_to(note_url)
```

### Step 2: 截图识别

```json
{"tool": "computer-mcp/inspect_screen", "params": {}}
```

### Step 3: AI 提取信息

AI 分析截图，提取：
- 笔记标题
- 正文内容
- 作者信息
- 点赞/收藏/评论数
- 发布时间

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| noteId | string | 是 | 笔记ID |

## 输出结果

```json
{
  "success": true,
  "noteId": "笔记ID",
  "screenshot_path": "D:\\...\\rednote_feed_xxx.png",
  "message": "请 AI 分析截图提取笔记详情"
}
```
