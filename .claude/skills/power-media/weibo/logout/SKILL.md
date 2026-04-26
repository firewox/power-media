---
name: weibo-logout
description: |
  使用 computer-mcp 退出微博登录。
  
  当用户说以下任何内容时触发此 skill：
  - "退出微博"
  - "微博登出"
  - "清除微博登录"
  - "logout weibo"
  - "微博退出登录"
  - 任何涉及退出微博登录的请求
  
  工作流程：
  1. 调用 computer-mcp/focus_window 聚焦微博窗口
  2. 调用 computer-mcp/inspect_screen 找到用户头像/设置菜单
  3. 调用 computer-mcp/click 点击头像/菜单
  4. 调用 computer-mcp/inspect_screen 找到退出选项
  5. 调用 computer-mcp/click 点击退出登录
  6. 调用 computer-mcp/confirm_action 确认退出
  7. 调用 computer-mcp/inspect_screen 验证退出成功
  
  依赖：
  - computer-mcp (focus_window, inspect_screen, click, confirm_action)
  - 已登录的微博浏览器窗口

compatibility:
  - computer-mcp >= 1.0
  - Windows 10/11
  - Edge / Chrome 浏览器
---

# 退出微博登录

## 工作流程（computer-mcp）

### Step 1: 聚焦微博窗口
```json
{
  "tool": "computer-mcp/focus_window",
  "params": {"title": "微博"}
}
```

### Step 2: 打开用户菜单
```json
{
  "tool": "computer-mcp/inspect_screen",
  "params": {}
}
```

找到用户头像或 "设置" 按钮并点击：
```json
{
  "tool": "computer-mcp/click",
  "params": {"x": <avatar_x>, "y": <avatar_y>}
}
```

### Step 3: 点击退出登录
```json
{
  "tool": "computer-mcp/inspect_screen",
  "params": {}
}
```

找到 "退出" 或 "退出登录" 并点击：
```json
{
  "tool": "computer-mcp/click",
  "params": {"x": <logout_x>, "y": <logout_y>}
}
```

### Step 4: 确认退出
```json
{
  "tool": "computer-mcp/confirm_action",
  "params": {"action_description": "确认退出微博登录？"}
}
```

### Step 5: 验证结果
检查是否回到登录页面（检测 "登录" 按钮）：
```json
{
  "tool": "computer-mcp/inspect_screen",
  "params": {}
}
```

## 输出结果

```json
{
  "success": true,
  "message": "已退出登录"
}
```

或

```json
{
  "success": false,
  "error": "退出失败"
}
```

## 使用示例

**示例 1：**
```
用户：退出微博
AI：
  1. 聚焦微博窗口
  2. 点击用户头像
  3. 点击退出登录
  4. 确认退出
结果：已退出登录
```

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 找不到菜单 | 提示用户页面可能已变化 |
| 未登录 | 返回提示未登录 |

## 注意事项

1. 退出后浏览器会清除登录会话
2. 下次使用需重新登录
3. 如需完全登出，请在微博网页手动操作
