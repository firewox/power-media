# RedNote (小红书) Skills - computer-mcp 版本

> 基于 computer-mcp 实现的小红书创作者平台自动化技能集合

---

## 概述

本目录包含 12 个小红书创作者平台的 Skills，全部基于 **computer-mcp** 实现，通过截图 + OCR 识别界面元素，使用鼠标点击和键盘输入模拟真实用户操作。

---

## 技术架构

### 核心组件

```
rednote/
├── lib/
│   ├── computer_mcp_client.py      # Computer MCP 客户端（复用 weibo 实现）
│   └── rednote_automation.py       # 小红书专用自动化封装
│
├── check-login/                    # 检查登录状态
├── get-qrcode/                     # 获取登录二维码
├── publish-note/                   # 发布图文笔记
├── publish-video/                  # 发布视频笔记
├── search/                         # 搜索内容
├── get-feed/                       # 获取帖子详情
├── get-profile/                    # 获取用户主页
├── like/                           # 点赞/取消点赞
├── favorite/                       # 收藏/取消收藏
├── comment/                        # 发表评论
└── reply/                          # 回复评论
```

### 技术方案

| 技术点 | 实现方案 |
|--------|---------|
| **浏览器控制** | 复用系统 Edge/Chrome 浏览器 |
| **登录管理** | 复用系统浏览器 Cookie，无需独立管理 |
| **元素定位** | 截图 + 多模态 AI 直接视觉理解 |
| **坐标系统** | 百分比坐标映射（适配不同分辨率） |
| **中文输入** | 剪贴板粘贴（Ctrl+V） |
| **登录判断** | 多模态 AI 直接视觉理解截图 |

---

## 快速开始

### 前置要求

1. **Python 依赖**:
```bash
pip install pyautogui pyperclip pywin32 pillow
```

2. **浏览器**: Edge 或 Chrome，已登录 creator.xiaohongshu.com

3. **computer-mcp**: 已配置并可用

### 使用示例

#### 1. 检查登录状态

```bash
python rednote/check-login/scripts/check_login.py
```

#### 2. 发布图文笔记

```bash
python rednote/publish-note/scripts/publish_note.py \
  --title "美食分享" \
  --content "今天做了一道超好吃的菜！#美食 #家常菜" \
  --images "photos/food1.jpg" "photos/food2.jpg" \
  --tags "#美食" "#家常菜"
```

#### 3. 搜索内容

```bash
python rednote/search/scripts/search.py --keyword "旅行攻略"
```

---

## Skills 列表

| Skill | 功能 | 触发条件 | 文档 |
|-------|------|---------|------|
| `rednote-check-login` | 检查登录状态 | "检查小红书登录状态" | [SKILL.md](check-login/SKILL.md) |
| `rednote-get-qrcode` | 获取登录二维码 | "获取小红书登录二维码" | [SKILL.md](get-qrcode/SKILL.md) |
| `rednote-publish-note` | 发布图文笔记 | "发布小红书笔记" | [SKILL.md](publish-note/SKILL.md) |
| `rednote-publish-video` | 发布视频笔记 | "发布小红书视频" | [SKILL.md](publish-video/SKILL.md) |
| `rednote-search` | 搜索内容 | "搜索小红书" | [SKILL.md](search/SKILL.md) |
| `rednote-get-feed` | 获取帖子详情 | "获取笔记详情" | [SKILL.md](get-feed/SKILL.md) |
| `rednote-get-profile` | 获取用户主页 | "获取用户主页" | [SKILL.md](get-profile/SKILL.md) |
| `rednote-like` | 点赞/取消点赞 | "点赞小红书" | [SKILL.md](like/SKILL.md) |
| `rednote-favorite` | 收藏/取消收藏 | "收藏小红书" | [SKILL.md](favorite/SKILL.md) |
| `rednote-comment` | 发表评论 | "评论小红书" | [SKILL.md](comment/SKILL.md) |
| `rednote-reply` | 回复评论 | "回复评论" | [SKILL.md](reply/SKILL.md) |

---

## 平台限制

| 限制项 | 数值 |
|--------|------|
| 标题长度 | ≤ 20 字 |
| 正文长度 | ≤ 1000 字 |
| 图片数量 | ≤ 18 张 |
| 视频大小 | ≤ 2GB |
| 视频时长 | 1 分钟 ~ 15 分钟 |
| 话题标签 | ≤ 10 个 |
| 日发布量 | 约 50 篇 |

---

## 迁移说明

本次迁移将 RedNote Skills 从 **Playwright** 迁移到 **computer-mcp**：

### 主要变化

| 维度 | 旧版 (Playwright) | 新版 (computer-mcp) |
|------|------------------|---------------------|
| **浏览器** | 独立 Chromium 实例 | 系统 Edge/Chrome |
| **元素定位** | DOM 选择器 | 截图 + OCR |
| **登录管理** | 独立 Cookie 文件 | 复用浏览器 Cookie |
| **坐标系统** | 不需要 | 百分比坐标映射 |
| **中文输入** | 直接输入 | 剪贴板粘贴 |

### 废弃文件

以下文件已不再使用（保留作为参考）：

- `lib/browser.js` - Playwright 浏览器管理
- `lib/cookie.js` - Cookie 管理
- `lib/system-browser.js` - 系统浏览器管理
- `lib/browser-connect.js` - 浏览器连接
- `test/*.js` - 旧测试文件

---

## 文档索引

| 文档 | 说明 |
|------|------|
| [迁移规格书](../../docs/superpowers/specs/2026-04-12-rednote-computer-mcp-migration.md) | 技术规格和迁移方案 |
| [实施计划](../../docs/superpowers/plans/2026-04-12-rednote-computer-mcp-migration.md) | 详细实施步骤 |
| [session-rednote.md](session-rednote.md) | 原始开发方案（旧版） |
| [TESTING.md](TESTING.md) | 测试规范（旧版，待更新） |

---

## 注意事项

1. **登录状态**: 依赖系统浏览器的登录态，如未登录需先扫码登录
2. **窗口状态**: 确保创作者平台页面已打开且未被最小化
3. **截图分析**: 所有登录状态判断、元素识别都由多模态 AI 直接视觉理解，无需 OCR
4. **安全确认**: 所有发布操作都需要人工确认
5. **频率控制**: 建议操作间添加随机延迟，模拟真实用户行为

---

*迁移完成时间: 2026-04-12*
*技术栈: computer-mcp + Python + 多模态 AI*
