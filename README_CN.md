# Power Media

> AI 驱动的社交媒体自动化管理平台 —— 基于 Claude Code / OpenCode 的技能系统与桌面控制 MCP 服务器。

## 概述

Power Media 是一套社交媒体自动化工具集，通过 **Claude Code Skills 系统** + **computer-mcp 桌面控制服务器**，让 AI 能够自动操作 Windows 桌面浏览器，实现多平台社交媒体的内容发布与管理。

### 核心架构

```
用户指令 → Claude Code / OpenCode
              ├── Skills 系统（场景化能力）
              │     ├── 微博 (浏览器自动化)
              │     ├── 小红书 (浏览器自动化)
              │     ├── 微信公众号 (官方 API)
              │     ├── 知乎 (规划中)
              │     └── check-ip (实用工具)
              │
              └── computer-mcp (MCP 服务器)
                    ├── 窗口管理 (list/focus)
                    ├── 屏幕截图 + OCR
                    ├── 鼠标/键盘模拟
                    └── 高风险操作确认守卫
```

### 两种工作模式

| 模式 | 适用平台 | 技术方案 |
|------|----------|----------|
| **浏览器自动化** | 微博、小红书 | computer-mcp 截图识别 + 模拟操作 |
| **API 直连** | 微信公众号 | 微信官方 HTTP API |

---

## 平台支持

### 微博 (Weibo)

通过 computer-mcp 控制浏览器完成操作。

| 技能 | 功能 | 状态 |
|------|------|------|
| `login` | 扫码登录微博 | ✅ |
| `logout` | 退出登录 | ✅ |
| `check-login` | 检查登录状态 | ✅ |
| `post-text` | 发布纯文本微博 (≤140字) | ✅ |
| `post-text-enhanced` | 增强版发博 (Ollama 视觉定位) | ✅ |
| `post-with-image` | 发布图文微博 | ✅ |

**技术细节：**
- 使用百分比坐标适配不同分辨率
- post-text-enhanced 版集成 Ollama 视觉模型，通过截图自动识别 UI 元素位置
- 基于 `WeiboAutomation` (computer_mcp_client.py) 封装

### 小红书 (RedNote / Xiaohongshu)

通过 computer-mcp 控制浏览器完成操作。

| 技能 | 功能 | 状态 |
|------|------|------|
| `get-qrcode` | 获取登录二维码 | ✅ |
| `check-login` | 检查登录状态 | ✅ |
| `get-feed` | 获取首页推荐内容 | ✅ |
| `get-profile` | 获取用户主页信息 | ✅ |
| `search` | 搜索笔记/用户 | ✅ |
| `like` | 点赞笔记 | ✅ |
| `favorite` | 收藏笔记 | ✅ |
| `comment` | 评论笔记 | ✅ |
| `reply` | 回复评论 | ✅ |
| `publish-note` | 发布图文笔记 | ✅ |
| `publish-video` | 发布视频笔记 | ✅ |

**技术细节：**
- 操作目标：小红书创作者平台 (`creator.xiaohongshu.com`) + 用户端 (`www.xiaohongshu.com`)
- 基于 `RedNoteAutomation` (rednote_automation.py) 封装
- 共享 `ComputerMCPClient` 与微博公共模块

### 微信公众号 (WeChat Official Account)

通过微信官方 HTTP API 直连，无需浏览器操作。

| 技能 | 功能 | 状态 |
|------|------|------|
| `test-connection` | 测试 API 连接 | ✅ |
| `upload-image` | 上传图片到素材库 | ✅ |
| `push-draft-text` | 推送文本/Markdown 到草稿箱 | ✅ |
| `push-draft-markdown` | 从文件推送文章到草稿箱 | ✅ |
| `get-draft-list` | 获取草稿列表 | ✅ |
| `get-draft-detail` | 获取草稿详情 | ✅ |
| `delete-draft` | 删除单篇草稿 | ✅ |
| `delete-all-drafts` | 清空草稿箱 | ✅ |
| `markdown-to-wechat-html` | Markdown 转微信兼容 HTML | ✅ |
| `validate-markdown` | 发布前预检 | ✅ |

**技术细节：**
- 通过 `api.weixin.qq.com` 官方 API 操作
- access_token 自动获取 + 内存缓存（提前 5 分钟刷新）
- 配置按优先级查找：`wechat-config.json` → `.env` → 环境变量
- 使用 `sharp` 生成 SVG 渐变封面图（自动备选方案）
- 代码语法高亮 + 微信兼容样式
- 内置错误码对照表和处理逻辑

### 知乎 (Zhihu)

计划中，尚未实现。

### check-ip

IP 查询工具，用于调试网络连接（如配置微信公众号 IP 白名单）。

---

## 环境要求

### 通用
- **操作系统**: Windows 10/11
- **终端**: PowerShell / bash

### computer-mcp 桌面控制
- **Python**: 3.8+
- **Node.js**: 可选（部分辅助脚本）
- **浏览器**: Edge / Chrome / Firefox（保持登录状态）
- **依赖安装**:
  ```bash
  cd computer-mcp
  pip install -r requirements.txt
  ```

#### 依赖清单
| 包名 | 用途 |
|------|------|
| `mcp` | MCP 服务器框架 |
| `pyautogui` | 鼠标/键盘模拟 |
| `pywinauto` | Windows GUI 自动化 |
| `mss` | 高性能屏幕截图 |
| `easyocr` | OCR 文字识别 |
| `opencv-python` | 图像处理 |
| `Pillow` | 图像处理 |

### 微信公众号 API
- **Node.js**: 18+
- **依赖安装**:
  ```bash
  cd .claude/skills/power-media/wechat
  npm install
  ```
- **依赖清单**: axios, form-data, marked, sanitize-html, highlight.js, sharp

---

## 快速开始

### 1. 启动 computer-mcp 服务器

```bash
cd computer-mcp
pip install -r requirements.txt
python server.py
```

### 2. 配置 MCP

在 `.claude/settings.local.json` 中添加：

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

### 3. 配置微信公众号凭据（可选）

创建 `.claude/skills/power-media/wechat/wechat-config.json`：

```json
{
  "WECHAT_APP_ID": "你的AppID",
  "WECHAT_APP_SECRET": "你的AppSecret",
  "WECHAT_DEFAULT_AUTHOR": "作者名",
  "WECHAT_NEED_OPEN_COMMENT": "true",
  "WECHAT_ONLY_FANS_CAN_COMMENT": "true"
}
```

---

## 安全设计

- **高风险操作确认**: 发帖、删除等关键操作需人工确认 (`confirm_guard.py`)
- **凭证分级存储**: 配置按 `config文件 → .env → 环境变量` 三级查找，不硬编码
- **Token 内存缓存**: access_token 仅存于进程内存，不落盘
- **日志脱敏**: 敏感参数通过 `secret=True` 标记在日志中自动隐藏
- **删除保护**: `delete-all-drafts` 要求显式确认参数

---

## 项目结构

```
power-media/
├── computer-mcp/                    # MCP 桌面控制服务器
│   ├── server.py                    # FastMCP 服务器入口
│   ├── windows_backend.py           # 窗口/鼠标/键盘操作
│   ├── screen_inspector.py          # 截图 + OCR
│   ├── confirm_guard.py             # 操作确认守卫
│   ├── logger.py                    # 操作日志（含脱敏）
│   ├── requirements.txt
│   └── tests/
│
└── .claude/skills/power-media/       # Skills 技能目录
    ├── check-ip/                     # IP 查询工具
    ├── computer-mcp/                 # computer-mcp 技能入口
    ├── weibo/                        # 微博技能组
    │   ├── lib/                      # 共享库
    │   │   ├── computer_mcp_client.py
    │   │   ├── screenshot_manager.py
    │   │   └── ollama_vision.py
    │   └── {login,logout,post-text,...}/
    ├── rednote/                      # 小红书技能组
    │   ├── lib/
    │   │   ├── rednote_automation.py
    │   │   └── computer_mcp_client.py
    │   └── {publish-note,search,...}/
    ├── wechat/                       # 微信公众号技能组
    │   ├── lib/
    │   │   └── wechat-common.js      # 共享库
    │   └── {test-connection,push-draft-text,...}/
    └── zhihu/                        # 知乎（规划中）
```

每个子技能的目录结构：
```
技能名/
├── SKILL.md          ← YAML 头描述 + Markdown 文档
├── README.md         ← 简要说明
└── scripts/
    └── 技能名.{py,js}  ← 核心实现代码
```

---

## 常见问题

**Q: 微博发帖失败？**
A: 确保浏览器已登录微博且 computer-mcp 正在运行。不同屏幕分辨率可能需要调整坐标参数。

**Q: 微信 API 返回 40001？**
A: 系统会自动刷新 access_token，如持续出现请检查 AppSecret 是否正确。

**Q: 图片上传失败？**
A: 检查图片格式（支持 JPG/PNG/GIF/BMP/WEBP）和大小（不超过 2MB），以及微信公众号后台 IP 白名单配置。

**Q: 提示缺少依赖？**
A: 运行相应平台的依赖安装脚本。Python 依赖：`pip install -r computer-mcp/requirements.txt`。WeChat Node.js 依赖：`cd .claude/skills/power-media/wechat && npm install`。
