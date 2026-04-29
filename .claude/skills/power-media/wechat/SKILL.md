---
name: wechat
description: |
  微信公众号文章管理与发布工具集 —— 从撰写到发布的全流程自动化。

  触发条件（满足任一即触发）：
  - 任何涉及微信公众号的操作：发布文章、管理草稿、上传素材、测试连接、格式转换
  - 用户提到「微信」「公众号」「草稿」「推送」「发布文章」「素材库」等关键词
  - 用户想「发一篇微信文章」「把文章推到公众号」「管理微信草稿箱」
  - 用户问「wechat 有什么功能」「微信配置怎么弄」

  集成的子能力：
  连接测试(test-connection) / 推送文本草稿(push-draft-text) / 推送文件草稿(push-draft-markdown)
  格式转换(markdown-to-wechat-html) / 发布预检(validate-markdown) / 上传图片(upload-image)
  草稿列表(get-draft-list) / 草稿详情(get-draft-detail) / 删除草稿(delete-draft) / 清空草稿(delete-all-drafts)

  ⚠️ 首次使用：如果未配置微信公众号凭据（WECHAT_APP_ID / WECHAT_APP_SECRET），
  必须引导用户完成配置后才能执行任何操作。详见 body 中的「首次使用引导」章节。

compatibility: |
  - Node.js 环境
  - 微信公众号 AppID 和 AppSecret
  - 依赖：axios, form-data, marked, sanitize-html, highlight.js, sharp
---

# 微信公众号文章管理与发布工具集

微信公众号操作的一站式工具集，覆盖从连接配置到内容发布的全流程。

---

## 🚀 首次使用引导

如果这是你第一次使用微信相关功能，按以下步骤操作：

### 第 1 步：获取凭据

登录[微信公众号后台](https://mp.weixin.qq.com) → 设置与开发 → 基本配置 → 获取 **AppID** 和 **AppSecret**。

### 第 2 步：选择配置方式（三选一）

**方式 A：让 AI 帮你创建配置文件（推荐）**

直接告诉我你的 AppID 和 AppSecret，我会自动创建 `.claude/skills/wechat/wechat-config.json`：

> 我的 AppID 是 wx1234567890，AppSecret 是 abc123def456

**方式 B：手动创建配置文件**

在 `.claude/skills/wechat/` 目录下创建 `wechat-config.json`：

```json
{
  "WECHAT_APP_ID": "wx1234567890abcdef",
  "WECHAT_APP_SECRET": "你的AppSecret",
  "WECHAT_DEFAULT_AUTHOR": "作者名",
  "WECHAT_NEED_OPEN_COMMENT": "true",
  "WECHAT_ONLY_FANS_CAN_COMMENT": "true"
}
```

**方式 C：使用环境变量**

```bash
export WECHAT_APP_ID="wx1234567890abcdef"
export WECHAT_APP_SECRET="你的AppSecret"
```

### 第 3 步：验证配置

对我说「测试微信连接」，确认配置正确。

### 配置项说明

| 配置项 | 必填 | 说明 |
|--------|------|------|
| `WECHAT_APP_ID` | ✅ 是 | 微信公众号 AppID |
| `WECHAT_APP_SECRET` | ✅ 是 | 微信公众号 AppSecret |
| `WECHAT_DEFAULT_AUTHOR` | 否 | 文章默认作者名 |
| `WECHAT_NEED_OPEN_COMMENT` | 否 | 是否开启评论（true/false） |
| `WECHAT_ONLY_FANS_CAN_COMMENT` | 否 | 仅粉丝可评论（true/false） |

### 配置文件优先级

系统按以下顺序查找凭据（找到即停）：

1. `.claude/skills/wechat/wechat-config.json`（推荐）
2. 项目根目录 `.env` 文件
3. 系统环境变量 `WECHAT_APP_ID` / `WECHAT_APP_SECRET`

---

## 📋 工作流程总览

```
配置凭据 → 测试连接 → 撰写/准备文章 → [可选: 预检] → 推送到草稿箱 → 管理草稿 → 发布
                ↑                               ↑
           test-connection              validate-markdown
                
中间环节：markdown-to-wechat-html（格式转换）、upload-image（上传图片素材）
管理操作：get-draft-list（列表）、get-draft-detail（详情）、delete-draft（删除）
```

---

## 🎯 快速开始

### 场景 1：我要发一篇文章

```
用户：推送一篇微信草稿，标题是「技术分享」，内容是「## 前言...」
```

AI 会自动：转换 Markdown → 处理图片 → 推送到草稿箱。

### 场景 2：从 Markdown 文件发布

```
用户：推送 ./posts/my-article.md 到微信草稿，标题是「深度学习入门」
```

AI 会自动：读取文件 → 转换 → 上传图片 → 生成封面 → 推送到草稿箱。

### 场景 3：查看和管理草稿

```
用户：获取微信草稿列表
用户：查看草稿详情 xxxxx
用户：删除草稿 xxxxx
```

---

## 🧩 子功能总览

### 🔌 连接与配置

| 子 Skill | 功能 | 触发短语示例 |
|----------|------|-------------|
| `test-connection` | 测试 API 连接 | 「测试微信连接」「检查微信配置」 |
| `validate-markdown` | 发布前预检 | 「发布前校验」「检查这篇文章能否发布」 |

### 📝 内容发布

| 子 Skill | 功能 | 触发短语示例 |
|----------|------|-------------|
| `push-draft-text` | 推送文本/Markdown 到草稿箱 | 「推送一篇微信草稿」「发布内容到公众号」 |
| `push-draft-markdown` | 从文件推送文章 | 「把 md 文件发布到微信草稿」「从文件创建微信文章」 |

### 📋 草稿管理

| 子 Skill | 功能 | 触发短语示例 |
|----------|------|-------------|
| `get-draft-list` | 获取草稿列表 | 「查看草稿箱」「列出微信草稿」 |
| `get-draft-detail` | 获取草稿详情 | 「查看草稿内容」「获取文章详情」 |
| `delete-draft` | 删除单篇草稿 | 「删除微信草稿」「删除这篇文章」 |
| `delete-all-drafts` | 清空草稿箱 | 「清空草稿箱」「删除所有草稿」 |

### 🖼️ 素材与转换

| 子 Skill | 功能 | 触发短语示例 |
|----------|------|-------------|
| `upload-image` | 上传图片到素材库 | 「上传图片到微信」「上传图片到素材库」 |
| `markdown-to-wechat-html` | Markdown 转微信 HTML | 「转换 markdown 生成 html」「markdown 转微信公众号格式」 |

---

## 🔧 子 Skill 详细说明

### test-connection — 连接测试

**用途**：首次配置后验证凭据是否正确。

**参数**：无

**输出示例**：
```json
{
  "success": true,
  "message": "微信 API 连接测试成功",
  "stage": "test-connection",
  "app_id": "wx...",
  "config_source": "environment"
}
```

### push-draft-text — 推送文本内容

**用途**：将一段文本或 Markdown 内容直接推送到微信公众号草稿箱。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `content` | string | 是 | 文章内容（文本或 Markdown） |
| `title` | string | 是 | 文章标题 |
| `digest` | string | 否 | 摘要（不填自动截取前 120 字） |
| `sourceUrl` | string | 否 | 原文链接 |

自动处理：Markdown → 微信兼容 HTML + 图片自动上传 + 代码语法高亮。

### push-draft-markdown — 推送 Markdown 文件

**用途**：读取本地 Markdown 文件，全自动推送到草稿箱。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `filePath` | string | 是 | Markdown 文件绝对路径 |
| `title` | string | 是 | 文章标题 |
| `digest` | string | 否 | 摘要 |
| `sourceUrl` | string | 否 | 原文链接 |

**封面图优先级**：文中第一张图 → 本地 thumbnail.png/jpg → 自动生成 SVG 渐变封面。

内部会先调用 `validate-markdown` 做预检，再执行推送。

### validate-markdown — 发布前校验

**用途**：在推送和发布前做全面检查，提前发现问题。

检查项：
- 微信凭据是否有效
- Markdown 文件是否存在且可读
- 本地图片路径是否有效
- access_token 是否能成功获取

### get-draft-list — 草稿列表

**参数**：`offset`（偏移，默认 0）、`count`（数量，默认 20，最大 20）

**返回**：草稿总数 + 每篇的 media_id、标题、作者、更新时间等。

### get-draft-detail — 草稿详情

**参数**：`mediaId`（草稿 ID）

**返回**：文章的完整内容，包括 HTML 正文、标题、作者、封面图等。

### delete-draft — 删除草稿

**参数**：`mediaId`（要删除的草稿 ID）

⚠️ 删除不可恢复，请确认后再操作。

### delete-all-drafts — 清空草稿箱

**参数**：`confirm`（必须设为 `true`）

⚠️ 会删除所有草稿！需要明确确认才会执行。

### upload-image — 上传图片

**参数**：`imageSource`（图片 URL 或本地路径）、`isTemporary`（是否临时素材，默认 false）

支持格式：JPG、PNG、GIF、BMP、WEBP。限制：单张不超过 2MB。

### markdown-to-wechat-html — 格式转换

**用途**：将 Markdown 文件转换为微信公众号兼容的 HTML（不推送到草稿箱）。

特性：代码语法高亮 / 微信兼容内联样式 / 列表转段落优化 / HTML 白名单过滤。

输出文件名：`原文件名-wechat.html`（如同目录生成）。

---

## ⚠️ 常见错误

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| `40001` | access_token 过期 | 自动重新获取，无需手动处理 |
| `40007` | 图片格式不正确 | 检查图片格式（JPG/PNG/GIF/BMP/WEBP） |
| `41005` | 图片数据为空 | 检查图片 URL 是否可访问或文件是否存在 |
| `45009` | 超过每日上传限制 | 减少上传频率，次日自动恢复 |
| `48001` | API 未授权 | 检查公众号权限和 IP 白名单 |

---

## 📌 注意事项

1. **IP 白名单**：确保服务器 IP 已在微信公众号后台 → 基本配置 → IP 白名单中配置
2. **Token 缓存**：access_token 自动缓存 2 小时，无需手动管理
3. **临时素材**：有效期 3 天，永久素材无过期限制
4. **草稿删除**：不可恢复，操作前请确认
5. **图片大小**：单张图片不超过 2MB，建议使用 JPG 格式

---

## 📦 依赖安装

```powershell
powershell -ExecutionPolicy Bypass -File .claude/skills/wechat/install-deps.ps1
```

核心依赖：axios、form-data、marked、sanitize-html、highlight.js、sharp
