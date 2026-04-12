---
name: rednote-favorite
description: |
  收藏/取消收藏小红书笔记。

  当用户说以下任何内容时触发此 skill：
  - "收藏小红书"
  - "给小红书收藏"
  - "取消收藏"
  - 任何涉及收藏小红书笔记的请求

  工作流程：
  1. 导航到笔记详情页
  2. 截图，多模态 AI 直接观察找到收藏按钮
  3. 点击收藏按钮
  4. 验证收藏状态

compatibility: |
  - computer-mcp >= 1.0
  - Windows 10/11
---

# 收藏/取消收藏

## 工作流程

与 `rednote-like` 类似，区别在于：

### Step 2: 截图识别收藏按钮

找到收藏按钮（星形图标）。

### Step 3: 点击收藏按钮

```json
{"tool": "computer-mcp/click", "params": {"x": detected_x, "y": detected_y}}
```

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| noteId | string | 是 | 笔记ID |
| unfavorite | boolean | 否 | 是否取消收藏，默认 false |

## 输出结果

```json
{
  "success": true,
  "noteId": "笔记ID",
  "action": "favorite/unfavorite",
  "screenshot_path": "D:\\...\\rednote_favorite_xxx.png",
  "message": "请 AI 分析截图并指导收藏操作"
}
```
