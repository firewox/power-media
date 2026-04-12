---
name: rednote-reply
description: |
  回复评论。

  当用户说以下任何内容时触发此 skill：
  - "回复评论"
  - "回复某条评论"
  - "回复小红书评论"
  - 任何涉及回复小红书评论的请求

  工作流程：
  1. 导航到笔记详情页
  2. 截图，多模态 AI 直接观察找到要回复的评论
  3. 点击"回复"按钮
  4. 输入回复内容
  5. 点击发送

compatibility: |
  - computer-mcp >= 1.0
  - Windows 10/11
---

# 回复评论

## 工作流程

与 `rednote-comment` 类似，区别在于：

### Step 2: 找到要回复的评论

滚动页面找到指定的评论。

### Step 3: 点击"回复"按钮

点击评论下方的"回复"链接。

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| noteId | string | 是 | 笔记ID |
| commentId | string | 是 | 评论ID |
| content | string | 是 | 回复内容 |

## 输出结果

```json
{
  "success": true,
  "noteId": "笔记ID",
  "commentId": "评论ID",
  "content": "回复内容",
  "screenshot_path": "D:\\...\\rednote_reply_xxx.png",
  "message": "请 AI 分析截图并指导回复操作"
}
```
