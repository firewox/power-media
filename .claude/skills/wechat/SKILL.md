---
name: wechat
description: |
  微信公众号文章管理发布与素材管理工具集。

  当用户需要操作微信公众号时触发此 skill：
  - 发布文章、管理草稿箱
  - 上传图片到素材库
  - 测试微信 API 连接
  - Markdown 转换为微信格式

  此 skill 集成了以下子功能：
  - test-connection: 测试微信公众号 API 连接
  - push-draft-text: 推送文本/Markdown 内容到草稿箱
  - push-draft-markdown: 从 Markdown 文件推送文章到草稿箱
  - validate-markdown: 发布前校验 Markdown、图片和 access_token
  - get-draft-list: 获取草稿箱文章列表
  - get-draft-detail: 获取草稿箱文章详情
  - delete-draft: 删除单篇草稿
  - delete-all-drafts: 批量删除所有草稿
  - upload-image: 上传图片到素材库
  - markdown-to-wechat-html: Markdown 转换为微信格式 HTML

  使用前必须配置微信公众号凭据（WECHAT_APP_ID, WECHAT_APP_SECRET）。

compatibility: |
  - Node.js 环境
  - 微信公众号 AppID 和 AppSecret
  - 依赖：axios, form-data, marked, sanitize-html, highlight.js, sharp
---

# 微信公众号文章管理发布与素材管理工具集

微信公众号操作的统一入口，提供文章发布、草稿管理、素材管理等功能。

## ⚠️ 重要：触发时必须检查配置

**每次触发此 skill 时，AI 必须首先执行以下检查：**

1. 检查 `.claude/skills/wechat/wechat-config.json` 文件是否存在
2. 检查项目根目录 `.env` 是否已设置
3. 检查环境变量 `WECHAT_APP_ID` 和 `WECHAT_APP_SECRET` 是否已设置

如果未检测到有效配置，**必须立即询问用户**选择以下方式之一：

---

**请选择微信公众号配置方式：**

1. **直接输入凭据** - 提供 AppID 和 AppSecret，AI 自动创建配置文件
2. **提供配置文件** - 在 `.claude/skills/wechat/` 目录下创建 `wechat-config.json` 文件
3. **系统环境变量** - 设置 `WECHAT_APP_ID` 和 `WECHAT_APP_SECRET` 环境变量
4. **其他方式** - 请说明您的配置需求

---

等待用户选择后再继续操作。

## 配置文件格式

### wechat-config.json 格式

```json
{
  "WECHAT_APP_ID": "wx7232333567cce",
  "WECHAT_APP_SECRET": "你的AppSecret",
  "WECHAT_DEFAULT_AUTHOR": "作者名",
  "WECHAT_NEED_OPEN_COMMENT": "true",
  "WECHAT_ONLY_FANS_CAN_COMMENT": "true"
}
```

**配置项说明：**

| 配置项 | 必填 | 说明 |
|--------|------|------|
| WECHAT_APP_ID | 是 | 微信公众号 AppID |
| WECHAT_APP_SECRET | 是 | 微信公众号 AppSecret |
| WECHAT_DEFAULT_AUTHOR | 否 | 默认作者名 |
| WECHAT_NEED_OPEN_COMMENT | 否 | 是否打开评论（true/false）|
| WECHAT_ONLY_FANS_CAN_COMMENT | 否 | 仅粉丝可评论（true/false）|

### 配置文件搜索路径（按优先级）

1. `.claude/skills/wechat/wechat-config.json`（推荐）
2. 项目根目录 `.env`
3. 环境变量 `WECHAT_APP_ID` / `WECHAT_APP_SECRET`

## 功能概览

| 功能 | 子 Skill | 说明 |
|------|----------|------|
| 连接测试 | `test-connection` | 测试微信公众号 API 连接 |
| 文章发布 | `push-draft-text` | 推送文本/Markdown 内容到草稿箱 |
| 文件发布 | `push-draft-markdown` | 从 Markdown 文件推送文章到草稿箱 |
| 发布预检 | `validate-markdown` | 校验 Markdown、图片和微信配置 |
| 草稿列表 | `get-draft-list` | 获取草稿箱文章列表 |
| 草稿详情 | `get-draft-detail` | 获取草稿箱文章详情 |
| 删除草稿 | `delete-draft` | 删除单篇草稿 |
| 清空草稿 | `delete-all-drafts` | 批量删除所有草稿 |
| 图片上传 | `upload-image` | 上传图片到素材库 |
| 格式转换 | `markdown-to-wechat-html` | Markdown 转换为微信格式 HTML |

## 子 Skill 详情

### test-connection - 连接测试

测试微信公众号 API 连接是否正常。

**输入：** 无

**输出：**
```json
{
  "success": true,
  "stage": "test-connection",
  "message": "微信 API 连接测试成功",
  "app_id": "wx...",
  "config_source": "environment"
}
```

### push-draft-text - 推送文本内容

推送文本/Markdown 内容到微信公众号草稿箱。

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | string | 是 | 文章内容（文本或 Markdown 格式）|
| title | string | 是 | 文章标题 |
| digest | string | 否 | 文章摘要（自动提取前 120 字）|
| sourceUrl | string | 否 | 原文链接 |

**特性：**
- 自动转换 Markdown 为微信兼容 HTML
- 自动处理网络图片并上传到素材库
- 代码块自动语法高亮

### push-draft-markdown - 推送 Markdown 文件

从 Markdown 文件推送文章到微信公众号草稿箱。

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| filePath | string | 是 | Markdown 文件绝对路径 |
| title | string | 是 | 文章标题 |
| digest | string | 否 | 文章摘要 |
| sourceUrl | string | 否 | 原文链接 |

**封面图优先级：**
1. 文章中的第一张图片
2. 本地 thumbnail.png/jpg 或 default-cover.png
3. 自动生成 SVG 渐变封面图

### validate-markdown - 发布前校验

在真正发布前执行预检：

- 校验配置来源是否有效
- 校验 Markdown 文件是否存在
- 校验本地图片路径是否可读
- 校验 access_token 是否可获取

### get-draft-list - 获取草稿列表

获取微信公众号草稿箱文章列表。

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| offset | number | 否 | 偏移位置，默认 0 |
| count | number | 否 | 返回数量，默认 20，最大 20 |

### get-draft-detail - 获取草稿详情

根据 media_id 获取草稿详情。

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| mediaId | string | 是 | 草稿的 media_id |

### delete-draft - 删除草稿

删除单篇草稿。

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| mediaId | string | 是 | 要删除的草稿 media_id |

### delete-all-drafts - 批量删除草稿

批量删除所有草稿（需确认）。

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| confirm | boolean | 是 | 必须设为 true 确认删除 |

### upload-image - 上传图片

上传图片到微信公众号素材库。

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| imageSource | string | 是 | 图片 URL 或本地文件路径 |
| isTemporary | boolean | 否 | 是否上传为临时素材（默认 false）|

**支持格式：** JPG, PNG, GIF, BMP, WEBP

**限制：** 图片大小不超过 2MB

### markdown-to-wechat-html - 格式转换

将 Markdown 文件转换为微信公众号兼容的 HTML 格式。

**特性：**
- 代码语法高亮
- 微信兼容样式
- 列表转段落优化
- HTML 白名单过滤

## 使用示例

**测试连接：**
```
用户：测试微信连接
结果：微信 API 连接测试成功
```

**推送文本内容：**
```
用户：推送一篇微信草稿，标题是"AI发展趋势"，内容是"## 人工智能的发展..."
结果：文章成功添加到草稿箱，media_id: xxxxx
```

**推送 Markdown 文件：**
```
用户：推送 ./article.md 到微信草稿，标题是"技术分享"
结果：文章成功添加到草稿箱，已处理图片 2 张
```

**查看草稿列表：**
```
用户：获取微信草稿列表
结果：共 50 篇草稿，返回前 20 篇...
```

**删除草稿：**
```
用户：删除微信草稿 xxxxx
结果：草稿删除成功
```

## 常见错误

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 40001 | access_token 过期 | 自动重新获取 |
| 40007 | 图片格式不正确 | 检查图片格式 |
| 41005 | 图片数据为空 | 检查图片 URL 或文件 |
| 45009 | 超过每日上传限制 | 减少上传频率 |
| 48001 | API 未授权 | 检查公众号权限 |

## 注意事项

1. **IP 白名单**：确保服务器 IP 已在微信公众号后台配置
2. **Token 缓存**：access_token 自动缓存，无需手动管理
3. **图片限制**：永久素材无过期时间，临时素材 3 天后过期
4. **草稿删除**：删除后无法恢复，请谨慎操作

## 依赖安装

```powershell
powershell -ExecutionPolicy Bypass -File D:\08_tmp\02_media\power-media\.claude\skills\wechat\install-deps.ps1
```

如需重新生成锁文件：

```powershell
powershell -ExecutionPolicy Bypass -File D:\08_tmp\02_media\power-media\.claude\skills\wechat\generate-lockfile.ps1
```

主要依赖：
- axios - HTTP 请求
- form-data - 文件上传
- marked - Markdown 解析
- sanitize-html - HTML 清理
- highlight.js - 代码高亮
- sharp - 图片处理
