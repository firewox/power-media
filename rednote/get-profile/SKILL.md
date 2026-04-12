---
name: rednote-get-profile
description: |
  获取用户主页信息。

  当用户说以下任何内容时触发此 skill：
  - "获取用户主页"
  - "查看用户资料"
  - "获取用户信息"
  - 任何涉及获取小红书用户主页的请求

  工作流程：
  1. 导航到用户主页
  2. 截图，多模态 AI 直接分析提取用户信息

compatibility: |
  - computer-mcp >= 1.0
  - Windows 10/11
---

# 获取用户主页

## 工作流程

### Step 1: 导航到用户主页

```python
profile_url = f"https://www.xiaohongshu.com/user/profile/{userId}"
automation.navigate_to(profile_url)
```

### Step 2: 截图识别

```json
{"tool": "computer-mcp/inspect_screen", "params": {}}
```

### Step 3: AI 提取信息

AI 分析截图，提取：
- 用户昵称
- 用户ID
- 粉丝数/关注数
- 笔记列表

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| userId | string | 是 | 用户ID |

## 输出结果

```json
{
  "success": true,
  "userId": "用户ID",
  "screenshot_path": "D:\\...\\rednote_profile_xxx.png",
  "message": "请 AI 分析截图提取用户信息"
}
```
