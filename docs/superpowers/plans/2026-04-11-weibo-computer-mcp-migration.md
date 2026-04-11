# Weibo Skills 迁移至 computer-mcp 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 Weibo skills 从 Playwright 迁移到 computer-mcp，实现基于截图+OCR的桌面浏览器自动化

**Architecture:** 移除所有 Node.js/Playwright 脚本，更新 SKILL.md 文件以描述基于 computer-mcp 的工作流程。每个 skill 直接调用 MCP 工具（screenshot, inspect_screen, click, type_text 等）操作桌面浏览器。

**Tech Stack:** computer-mcp (MCP Server), Windows Desktop, Edge/Chrome 浏览器

---

## 文件结构

### 修改的文件
- `weibo/check-login/SKILL.md` - 更新为 computer-mcp 工作流程
- `weibo/login/SKILL.md` - 更新为 computer-mcp 工作流程
- `weibo/logout/SKILL.md` - 更新为 computer-mcp 工作流程
- `weibo/post-text/SKILL.md` - 更新为 computer-mcp 工作流程
- `weibo/post-with-image/SKILL.md` - 更新为 computer-mcp 工作流程
- `weibo/README.md` - 更新平台使用指南

### 删除的文件
- `weibo/check-login/scripts/check-login.js`
- `weibo/login/scripts/login.js`
- `weibo/logout/scripts/logout.js`
- `weibo/post-text/scripts/post-text.js`
- `weibo/post-with-image/scripts/post-with-image.js`
- `weibo/lib/weibo.js`
- `weibo/*/scripts/` 目录

---

## Phase 1: 基础 Skill 迁移

### Task 1: 备份并删除旧 Playwright 代码

**Files:**
- Delete: `weibo/check-login/scripts/check-login.js`
- Delete: `weibo/login/scripts/login.js`
- Delete: `weibo/logout/scripts/logout.js`
- Delete: `weibo/lib/weibo.js`
- Delete: `weibo/*/scripts/` 目录

- [ ] **Step 1: 查看当前 weibo 目录结构**

Run: `ls -la weibo/`
Expected: 显示 check-login, login, logout, post-text, post-with-image, lib 目录

- [ ] **Step 2: 删除 check-login/scripts 目录**

```bash
cd weibo/check-login
rm -rf scripts/
ls -la
```
Expected: scripts 目录已删除，只剩 SKILL.md

- [ ] **Step 3: 删除 login/scripts 目录**

```bash
cd ../login
rm -rf scripts/
ls -la
```
Expected: scripts 目录已删除

- [ ] **Step 4: 删除 logout/scripts 目录**

```bash
cd ../logout
rm -rf scripts/
ls -la
```
Expected: scripts 目录已删除

- [ ] **Step 5: 删除 lib 目录**

```bash
cd ..
rm -rf lib/
ls -la
```
Expected: lib 目录已删除

- [ ] **Step 6: Commit**

```bash
cd ../..
git add weibo/
git commit -m "chore(weibo): remove Playwright scripts and lib directory

- Delete all scripts/ directories from check-login, login, logout
- Delete weibo/lib/weibo.js shared library
- Prepare for computer-mcp migration"
```

---

### Task 2: 更新 weibo-check-login SKILL.md

**Files:**
- Modify: `weibo/check-login/SKILL.md`

- [ ] **Step 1: 读取当前 SKILL.md**

Run: `cat weibo/check-login/SKILL.md`
Expected: 显示当前 Playwright 版本的 skill 定义

- [ ] **Step 2: 重写 SKILL.md 为 computer-mcp 版本**

```markdown
---
name: weibo-check-login
description: |
  使用 computer-mcp 检查微博登录状态。
  
  触发条件：
  - "检查微博登录状态"
  - "weibo check login"
  - "微博登录了吗"
  
  工作流程：
  1. 调用 computer-mcp/focus_window 聚焦微博窗口
  2. 调用 computer-mcp/inspect_screen 识别界面元素
  3. 分析 OCR 结果判断登录状态
  4. 返回登录状态和用户名
  
  依赖：
  - computer-mcp (focus_window, inspect_screen)
  - 已打开的微博浏览器窗口

compatibility:
  - computer-mcp >= 1.0
  - Windows 10/11
  - Edge / Chrome 浏览器
---

# 检查微博登录状态

## 工作流程（computer-mcp）

### Step 1: 聚焦微博窗口
```json
{
  "tool": "computer-mcp/focus_window",
  "params": {"title": "微博"}
}
```

### Step 2: 截图并识别界面
```json
{
  "tool": "computer-mcp/inspect_screen",
  "params": {}
}
```

### Step 3: 分析登录状态
从 OCR 结果中检查：
- 未登录：检测到 "登录" / "注册" 按钮
- 已登录：检测到用户名（如 "xxx 的微博"）

## 输出结果

```json
{
  "loggedIn": true,
  "userName": "xxx"
}
```

或

```json
{
  "loggedIn": false,
  "userName": null
}
```

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 找不到微博窗口 | 提示用户先打开浏览器访问 weibo.com |
| OCR 识别失败 | 重试截图，最多 3 次 |

## 注意事项

1. 必须先打开浏览器并访问 weibo.com
2. 确保微博窗口未被最小化
```

- [ ] **Step 3: 验证文件内容**

Run: `cat weibo/check-login/SKILL.md`
Expected: 显示新的 computer-mcp 版本内容

- [ ] **Step 4: Commit**

```bash
git add weibo/check-login/SKILL.md
git commit -m "docs(weibo): migrate check-login skill to computer-mcp

- Remove Playwright-based workflow
- Add computer-mcp based workflow with screenshot + OCR
- Update description and compatibility"
```

---

### Task 3: 更新 weibo-login SKILL.md

**Files:**
- Modify: `weibo/login/SKILL.md`

- [ ] **Step 1: 读取当前 SKILL.md**

Run: `cat weibo/login/SKILL.md`

- [ ] **Step 2: 重写 SKILL.md 为 computer-mcp 版本**

```markdown
---
name: weibo-login
description: |
  使用 computer-mcp 完成微博扫码登录。
  
  触发条件：
  - "登录微博"
  - "weibo login"
  - "微博扫码登录"
  
  工作流程：
  1. 调用 computer-mcp/focus_window 聚焦浏览器窗口
  2. 调用 computer-mcp 键盘快捷键访问 weibo.com
  3. 调用 computer-mcp/inspect_screen 找到扫码登录入口
  4. 调用 computer-mcp/click 切换到扫码登录
  5. 等待用户扫码完成
  6. 调用 computer-mcp/inspect_screen 验证登录成功
  
  依赖：
  - computer-mcp (focus_window, inspect_screen, click, type_text, hotkey)
  - Edge / Chrome 浏览器

compatibility:
  - computer-mcp >= 1.0
  - Windows 10/11
  - Edge / Chrome 浏览器
---

# 微博扫码登录

## 工作流程（computer-mcp）

### Step 1: 聚焦浏览器窗口
```json
{
  "tool": "computer-mcp/focus_window",
  "params": {"title": "Edge"}
}
```

### Step 2: 访问微博登录页
```json
{
  "tool": "computer-mcp/hotkey",
  "params": {"keys": ["ctrl", "l"]}
}
```

```json
{
  "tool": "computer-mcp/type_text",
  "params": {"text": "weibo.com"}
}
```

```json
{
  "tool": "computer-mcp/press_key",
  "params": {"key": "enter"}
}
```

### Step 3: 切换到扫码登录
```json
{
  "tool": "computer-mcp/inspect_screen",
  "params": {}
}
```

从 OCR 结果中找到 "扫码登录" 坐标并点击：
```json
{
  "tool": "computer-mcp/click",
  "params": {"x": <detected_x>, "y": <detected_y>}
}
```

### Step 4: 等待用户扫码
显示二维码，提示用户使用手机微博 APP 扫码。

```json
{
  "tool": "computer-mcp/wait",
  "params": {"seconds": 3}
}
```

### Step 5: 验证登录成功
循环检查登录状态（最多 2 分钟）：
```json
{
  "tool": "computer-mcp/inspect_screen",
  "params": {}
}
```

检测到用户名即表示登录成功。

## 输出结果

```json
{
  "success": true,
  "userName": "xxx",
  "message": "登录成功"
}
```

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 找不到浏览器窗口 | 提示用户打开 Edge/Chrome |
| 二维码超时 | 提示刷新页面重试 |
| 用户取消登录 | 返回取消状态 |

## 注意事项

1. 二维码有效期约 2 分钟
2. 需使用手机微博 APP 扫码
3. 登录会话保存在浏览器中
```

- [ ] **Step 3: 验证文件**

Run: `cat weibo/login/SKILL.md | head -20`
Expected: 显示新的 YAML frontmatter

- [ ] **Step 4: Commit**

```bash
git add weibo/login/SKILL.md
git commit -m "docs(weibo): migrate login skill to computer-mcp

- Remove Playwright-based workflow
- Add computer-mcp based login workflow
- Include step-by-step MCP tool calls"
```

---

## Phase 2: 发布 Skill 迁移

### Task 4: 更新 weibo-post-text SKILL.md

**Files:**
- Modify: `weibo/post-text/SKILL.md`
- Delete: `weibo/post-text/scripts/` 目录

- [ ] **Step 1: 删除 post-text/scripts 目录**

```bash
cd weibo/post-text
rm -rf scripts/
ls -la
```
Expected: scripts 目录已删除

- [ ] **Step 2: 读取当前 SKILL.md**

Run: `cat SKILL.md`

- [ ] **Step 3: 重写 SKILL.md 为 computer-mcp 版本**

```markdown
---
name: weibo-post-text
description: |
  使用 computer-mcp 发布纯文本微博。
  
  触发条件：
  - "发微博"
  - "发布微博"
  - "post weibo"
  - "发一条微博"
  
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

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 未登录 | 返回错误，提示先执行 weibo-login |
| 找不到输入框 | 重试截图，或提示用户检查页面 |
| 内容超长 | Skill 层校验，拒绝执行 |
| 发送失败 | 返回错误信息 |

## 注意事项

1. 必须先打开浏览器并访问 weibo.com
2. 确保微博窗口未被最小化
3. 内容长度限制 140 字符
4. 高风险操作需人工确认
```

- [ ] **Step 4: 验证文件**

Run: `cat weibo/post-text/SKILL.md | head -30`
Expected: 显示新的 computer-mcp 工作流程

- [ ] **Step 5: Commit**

```bash
cd ../..
git add weibo/post-text/
git commit -m "docs(weibo): migrate post-text skill to computer-mcp

- Remove Playwright scripts directory
- Update SKILL.md with computer-mcp workflow
- Add confirm_action for safety"
```

---

### Task 5: 更新 weibo-post-with-image SKILL.md

**Files:**
- Modify: `weibo/post-with-image/SKILL.md`
- Delete: `weibo/post-with-image/scripts/` 目录

- [ ] **Step 1: 删除 post-with-image/scripts 目录**

```bash
cd weibo/post-with-image
rm -rf scripts/
ls -la
```

- [ ] **Step 2: 读取当前 SKILL.md**

Run: `cat SKILL.md`

- [ ] **Step 3: 重写 SKILL.md 为 computer-mcp 版本**

```markdown
---
name: weibo-post-with-image
description: |
  使用 computer-mcp 发布带图片的微博。
  
  触发条件：
  - "发微博带图"
  - "发布图文微博"
  - "post weibo with image"
  
  工作流程：
  1. 调用 weibo-check-login 确认已登录
  2. 调用 computer-mcp/focus_window 聚焦微博窗口
  3. 调用 computer-mcp/inspect_screen 识别输入框
  4. 调用 computer-mcp/click 点击输入框
  5. 调用 computer-mcp/type_text 输入内容
  6. 调用 computer-mcp/inspect_screen 找到图片按钮
  7. 调用 computer-mcp/click 点击添加图片
  8. 调用 computer-mcp/type_text 输入图片路径
  9. 调用 computer-mcp 等待上传完成
  10. 调用 computer-mcp/click 点击发送
  11. 调用 computer-mcp/confirm_action 确认发布
  12. 调用 computer-mcp/inspect_screen 验证发布成功
  
  依赖：
  - computer-mcp (focus_window, inspect_screen, click, type_text, confirm_action, wait)
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
找到 "发送" 按钮并点击。

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

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 图片不存在 | 返回错误，提示检查路径 |
| 上传失败 | 重试或返回错误 |
| 格式不支持 | 提示支持的格式 |

## 注意事项

1. 图片路径需使用绝对路径或相对于工作目录的路径
2. 上传大图片可能需要更长时间
3. 最多支持 9 张图片
```

- [ ] **Step 4: 验证文件**

Run: `cat weibo/post-with-image/SKILL.md | grep "computer-mcp" | head -5`
Expected: 显示多个 computer-mcp 工具引用

- [ ] **Step 5: Commit**

```bash
cd ../..
git add weibo/post-with-image/
git commit -m "docs(weibo): migrate post-with-image skill to computer-mcp

- Remove Playwright scripts directory
- Update SKILL.md with computer-mcp workflow
- Include image upload workflow"
```

---

## Phase 3: 清理与文档

### Task 6: 更新 weibo-logout SKILL.md

**Files:**
- Modify: `weibo/logout/SKILL.md`
- Delete: `weibo/logout/scripts/` 目录（如存在）

- [ ] **Step 1: 确认 scripts 目录已删除**

```bash
ls -la weibo/logout/
```
Expected: 只有 SKILL.md

- [ ] **Step 2: 读取当前 SKILL.md**

Run: `cat weibo/logout/SKILL.md`

- [ ] **Step 3: 重写 SKILL.md 为 computer-mcp 版本**

```markdown
---
name: weibo-logout
description: |
  使用 computer-mcp 退出微博登录。
  
  触发条件：
  - "退出微博"
  - "weibo logout"
  - "微博退出登录"
  
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
检查是否回到登录页面（检测 "登录" 按钮）。

## 输出结果

```json
{
  "success": true,
  "message": "已退出登录"
}
```

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 找不到菜单 | 提示用户页面可能已变化 |
| 未登录 | 返回提示未登录 |

## 注意事项

1. 退出后浏览器会清除登录会话
2. 下次使用需重新登录
```

- [ ] **Step 4: 验证文件**

Run: `cat weibo/logout/SKILL.md | head -25`
Expected: 显示新的 YAML frontmatter 和工作流程

- [ ] **Step 5: Commit**

```bash
git add weibo/logout/SKILL.md
git commit -m "docs(weibo): migrate logout skill to computer-mcp

- Update SKILL.md with computer-mcp workflow
- Add confirm_action for safety"
```

---

### Task 7: 更新 weibo/README.md

**Files:**
- Create/Modify: `weibo/README.md`

- [ ] **Step 1: 检查当前是否有 README.md**

```bash
ls -la weibo/README.md 2>/dev/null && echo "exists" || echo "not exists"
```

- [ ] **Step 2: 创建/更新 README.md**

```markdown
# Weibo 微博 Skills

使用 computer-mcp 自动化操作桌面浏览器中的微博网页版。

## 前置要求

1. **系统环境**
   - Windows 10/11
   - Edge 或 Chrome 浏览器

2. **MCP 配置**
   确保 `.claude/settings.local.json` 中已配置：
   ```json
   {
     "mcpServers": {
       "computer": {
         "command": "python",
         "args": ["computer-mcp/server.py"]
       }
     }
   }
   ```

3. **浏览器准备**
   - 打开浏览器
   - 访问 https://weibo.com
   - 保持窗口可见（不要最小化）

## Skills 列表

| Skill | 功能 | 触发词 |
|-------|------|--------|
| `weibo-check-login` | 检查登录状态 | "检查微博登录" |
| `weibo-login` | 扫码登录 | "登录微博" |
| `weibo-logout` | 退出登录 | "退出微博" |
| `weibo-post-text` | 发布纯文本微博 | "发微博" |
| `weibo-post-with-image` | 发布带图微博 | "发微博带图" |

## 使用流程

### 1. 首次使用

```
登录微博
```

AI 会：
1. 打开浏览器访问 weibo.com
2. 切换到扫码登录
3. 提示你使用手机 APP 扫码
4. 等待登录完成

### 2. 发布微博

```
发微博：今天天气真好！
```

AI 会：
1. 检查登录状态
2. 聚焦微博窗口
3. 点击输入框
4. 输入内容
5. 点击发送
6. 确认发布

### 3. 发布带图微博

```
发微博带图，文字是"测试图片"，图片是 C:\Users\xxx\Pictures\test.jpg
```

## 工作原理

这些 skills 使用 **computer-mcp** 进行桌面自动化：

1. **截图识别** - 使用 `inspect_screen` 获取界面文字和位置
2. **窗口管理** - 使用 `focus_window` 聚焦浏览器窗口
3. **模拟操作** - 使用 `click`, `type_text`, `hotkey` 模拟用户操作
4. **安全确认** - 使用 `confirm_action` 确保高风险操作需人工确认

不再使用 Playwright，无需维护 DOM 选择器，更加稳定可靠。

## 故障排查

### 找不到微博窗口
- 确保浏览器已打开
- 确保访问了 weibo.com
- 确保窗口标题包含"微博"

### OCR 识别失败
- 确保窗口未被其他窗口遮挡
- 尝试放大浏览器窗口
- 检查 computer-mcp 是否正常运行

### 点击位置不准确
- OCR 返回的是文字区域，点击位置可能有偏差
- 技能会自动调整偏移量
- 如持续失败，可手动操作后让 AI 继续

## 技术架构

```
用户请求
    ↓
Weibo Skill (SKILL.md 描述)
    ↓
computer-mcp (MCP Server)
    ├── screenshot / inspect_screen
    ├── focus_window
    ├── click / type_text / hotkey
    └── confirm_action
    ↓
桌面浏览器 (用户已打开的窗口)
```

## 迁移说明

本项目已从 Playwright 迁移到 computer-mcp：
- ❌ 不再使用 Node.js/Playwright 脚本
- ❌ 不再依赖 DOM 选择器
- ✅ 使用截图+OCR 识别界面
- ✅ 操作真实桌面浏览器窗口
```

- [ ] **Step 3: 验证文件**

Run: `cat weibo/README.md | head -40`
Expected: 显示完整的平台使用指南

- [ ] **Step 4: Commit**

```bash
git add weibo/README.md
git commit -m "docs(weibo): add platform README for computer-mcp

- Document prerequisites and setup
- List all available skills
- Explain computer-mcp workflow
- Add troubleshooting guide"
```

---

### Task 8: 最终验证与集成测试

**Files:**
- All `weibo/*/SKILL.md` files

- [ ] **Step 1: 验证所有 scripts 目录已删除**

```bash
find weibo -type d -name "scripts"
```
Expected: 无输出（没有 scripts 目录）

- [ ] **Step 2: 验证所有 SKILL.md 包含 computer-mcp**

```bash
grep -l "computer-mcp" weibo/*/SKILL.md
```
Expected: 显示所有 5 个 skill 的 SKILL.md 文件

- [ ] **Step 3: 验证 lib 目录已删除**

```bash
ls weibo/lib/ 2>/dev/null && echo "exists" || echo "deleted"
```
Expected: "deleted"

- [ ] **Step 4: 检查 git 状态**

```bash
git status
```
Expected: 无未提交的修改

- [ ] **Step 5: 创建集成测试标签**

```bash
git tag -a v1.0.0-mcp-migration -m "Weibo skills migrated to computer-mcp

- Removed all Playwright scripts
- Updated all SKILL.md to use computer-mcp
- Added platform README"
```

- [ ] **Step 6: 最终 Commit（如有未提交的修改）**

```bash
git add -A
git commit -m "chore(weibo): complete computer-mcp migration

- All 5 skills migrated from Playwright to computer-mcp
- All scripts directories removed
- Platform README added
- Ready for testing"
```

---

## 验收检查清单

实施完成后，验证以下项目：

### 文件结构
- [ ] `weibo/check-login/scripts/` 已删除
- [ ] `weibo/login/scripts/` 已删除
- [ ] `weibo/logout/scripts/` 已删除
- [ ] `weibo/post-text/scripts/` 已删除
- [ ] `weibo/post-with-image/scripts/` 已删除
- [ ] `weibo/lib/` 已删除
- [ ] `weibo/README.md` 已创建

### SKILL.md 更新
- [ ] `weibo/check-login/SKILL.md` 包含 computer-mcp 工作流程
- [ ] `weibo/login/SKILL.md` 包含 computer-mcp 工作流程
- [ ] `weibo/logout/SKILL.md` 包含 computer-mcp 工作流程
- [ ] `weibo/post-text/SKILL.md` 包含 computer-mcp 工作流程
- [ ] `weibo/post-with-image/SKILL.md` 包含 computer-mcp 工作流程

### Git 状态
- [ ] 所有修改已提交
- [ ] 提交信息符合规范
- [ ] 工作目录干净

---

## 附录

### A. 旧代码备份（可选）

如需保留旧 Playwright 代码作为参考，可在删除前创建备份分支：

```bash
git checkout -b backup/playwright-weibo
git checkout master
# 然后继续迁移
```

### B. 回滚方案

如需回滚到 Playwright 版本：

```bash
git log --oneline --grep="Playwright"
# 找到最后一个包含 Playwright 代码的提交
git checkout <commit-hash> -- weibo/
```

### C. 相关文档

- [Agent 调用协议](../../AGENT-CALLING-PROTOCOL.md)
- [迁移技术规格](../specs/2026-04-11-weibo-computer-mcp-migration.md)
- [computer-mcp 工具文档](../../../computer-mcp/server.py)

---

**计划版本**: 1.0  
**创建日期**: 2026-04-11  
**状态**: Ready for Implementation
