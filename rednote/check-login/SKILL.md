---
name: rednote-check-login
description: |
  检查小红书创作者平台登录状态。

  当用户说以下任何内容时触发此 skill：
  - "检查小红书登录状态"
  - "小红书登录了吗"
  - "查看小红书是否登录"
  - "检查登录状态"
  - 任何涉及检查小红书账号登录状态的请求

  工作流程：
  1. 聚焦/打开创作者平台窗口
  2. 截图当前页面
  3. 多模态 AI 直接分析截图判断登录状态（无需 OCR）

  依赖：
  - computer-mcp (screenshot, focus_window)
  - 多模态 AI 模型（视觉理解能力）
  - 浏览器已打开 creator.xiaohongshu.com 页面

compatibility: |
  - computer-mcp >= 1.0
  - Windows 10/11
  - Edge / Chrome 浏览器
  - Python 3.8+
---

# 检查小红书创作者平台登录状态

## 工作流程

### Step 1: 聚焦创作者平台窗口

使用 `rednote_automation.find_or_open_creator()` 自动查找或打开小红书创作者平台窗口。

或手动调用 computer-mcp：
```json
{"tool": "computer-mcp/focus_window", "params": {"title": "小红书创作者中心"}}
```

### Step 2: 截图

```json
{"tool": "computer-mcp/inspect_screen", "params": {}}
```

返回截图路径，供多模态 AI 直接分析。

### Step 3: 多模态 AI 分析登录状态

多模态 AI 直接观察截图，判断：
- **已登录**: 看到右上角有用户头像/昵称
- **未登录**: 看到登录二维码/登录按钮

## 输入参数

无必需参数。

## 输出结果

**成功（已登录）**:
```json
{
  "success": true,
  "loggedIn": true,
  "screenshot_path": "D:\\...\\rednote_shot_xxx.png"
}
```

**成功（未登录）**:
```json
{
  "success": true,
  "loggedIn": false,
  "screenshot_path": "D:\\...\\rednote_shot_xxx.png",
  "message": "未登录，请扫码登录"
}
```

**失败**:
```json
{
  "success": false,
  "error": "无法打开创作者平台窗口"
}
```

## 配置要求

环境变量：
- 无特殊要求

## 使用示例

```
用户：检查小红书登录状态
结果：已登录，截图路径: D:\...\rednote_shot_xxx.png

用户：小红书登录了吗
结果：未登录，请执行 rednote-get-qrcode 获取登录二维码
```

## 注意事项

1. 需要浏览器已打开创作者平台页面（如未打开会自动打开）
2. Cookie 有效期通常为几天到几周，过期后需重新登录
3. 同一账号只能在一个浏览器实例中保持登录状态
4. 截图由多模态 AI 直接视觉理解判断登录状态，无需 OCR
