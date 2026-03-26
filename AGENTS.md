# Power Media - AI 新媒体超级工具箱

## Skill 加载规则

**重要**: 本项目只使用项目本地 skills，不加载全局 skills。

- **忽略** `~/.config/opencode/skills/` 下的所有 skills
- **只从** `./.claude/skills/` 加载 skills

当需要使用 skill 时，优先从项目本地 `.claude/skills/` 目录查找和使用。

---

## 项目概述

Power Media 是一个基于 **Claude Code Skills** 构建的 AI 新媒体集成工具箱。通过构建自定义 Skills，让 AI 能够与多种主流新媒体平台进行交互，实现内容的自动化发布、管理和运营。

**核心设计理念**: 将每个新媒体平台的操作封装为可复用的 Skill，通过统一的接口调用，实现 AI 对多平台的无缝操作。

---

## 项目架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        Claude Code                               │
│                     (AI Assistant)                               │
└─────────────────────────┬───────────────────────────────────────┘
                          │ Skill 调用
┌─────────────────────────▼───────────────────────────────────────┐
│                      Skills 层                                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│  │ 微信公众号    │ │    微博      │ │   小红书     │  ...        │
│  │   Skill      │ │   Skill      │ │   Skill      │             │
│  └──────────────┘ └──────────────┘ └──────────────┘             │
└─────────────────────────┬───────────────────────────────────────┘
                          │ API 调用
┌─────────────────────────▼───────────────────────────────────────┐
│                     新媒体平台                                   │
│    微信公众号   微博   小红书   头条   抖音   B站   知乎          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Skills 目录结构

```
power-media/
├── skills/
│   ├── wechat-official-account/    # 微信公众号
│   │   ├── skill.yaml              # Skill 定义
│   │   └── wechat-api.js           # API 实现
│   ├── weibo/                      # 微博
│   │   ├── skill.yaml
│   │   └── weibo-api.js
│   ├── xiaohongshu/                # 小红书
│   │   ├── skill.yaml
│   │   └── xiaohongshu-api.js
│   ├── toutiao/                    # 今日头条
│   │   ├── skill.yaml
│   │   └── toutiao-api.js
│   ├── douyin/                     # 抖音
│   │   ├── skill.yaml
│   │   └── douyin-api.js
│   ├── bilibili/                   # Bilibili
│   │   ├── skill.yaml
│   │   └── bilibili-api.js
│   └── zhihu/                      # 知乎
│       ├── skill.yaml
│       └── zhihu-api.js
├── .claude/
│   └── settings.local.json         # 项目配置
├── Agent.md                        # 项目说明
└── memory/
    └── MEMORY.md                   # 项目记忆
```

---

## 平台接入状态

| 平台 | Skill 名称 | 功能 | 状态 |
|------|-----------|------|------|
| 微信公众号 | `wechat-official-account` | 发布文章、素材管理、草稿管理 | 🚧 开发中 |
| 微博 | `weibo` | 发布微博、图文、获取时间线 | 📋 规划中 |
| 小红书 | `xiaohongshu` | 发布图文/视频笔记 | 📋 规划中 |
| 今日头条 | `toutiao` | 发布文章、微头条 | 📋 规划中 |
| 抖音 | `douyin` | 发布图文视频、管理作品 | 📋 规划中 |
| Bilibili | `bilibili` | 发布视频、动态 | 📋 规划中 |
| 知乎 | `zhihu` | 发布回答、文章、想法 | 📋 规划中 |

---

## Skill 定义规范

每个 Skill 由两部分组成：

### 1. skill.yaml - Skill 元数据和指令

```yaml
name: wechat-official-account
version: 1.0.0
description: 微信公众号内容发布和管理

# Skill 指令
instructions: |
  你有一个微信公众号管理工具，可以执行以下操作：
  - 发布文章到草稿箱
  - 获取草稿列表
  - 删除草稿
  - 上传图片素材

  当用户要求发布文章时：
  1. 生成或获取文章内容（支持 Markdown 格式）
  2. 调用 wechat:push-draft 发布到草稿箱
  3. 返回发布结果和文章链接

# 可用工具
tools:
  - name: wechat:push-draft
    description: 推送文章到微信公众号草稿箱
    args:
      - title: 文章标题
      - content: 文章内容（支持 Markdown）
      - digest: 文章摘要（可选）
      - cover_image: 封面图片 URL（可选）

  - name: wechat:get-drafts
    description: 获取草稿箱列表
    args:
      - offset: 偏移量（默认 0）
      - count: 数量（默认 20）

  - name: wechat:delete-draft
    description: 删除草稿
    args:
      - media_id: 草稿媒体 ID

# 环境变量要求
env:
  - WECHAT_APP_ID: 微信公众号 AppID
  - WECHAT_APP_SECRET: 微信公众号 AppSecret
```

### 2. API 实现文件

根据平台特性，使用以下技术栈实现：

- **Node.js**: `wechat-api.js` - 适合微信等有官方 SDK 的平台
- **Python**: `wechat_api.py` - 适合需要爬虫或自动化操作的平台
- **Playwright**: 自动化浏览器操作 - 适合没有开放 API 的平台（如小红书）

---

## 开发路线图

### Phase 1: 微信公众号 (已完成基础接入)
- [x] 分析微信 API 接口
- [ ] 创建 `wechat-official-account/skill.yaml`
- [ ] 实现 `wechat-api.js` - 核心 API 封装
- [ ] 测试文章发布流程

### Phase 2: 图文平台
- [ ] **微博**: 发布微博、图文、评论管理
- [ ] **小红书**: 图文笔记发布（需模拟登录或使用第三方 API）
- [ ] **知乎**: 文章、回答、想法发布

### Phase 3: 视频平台
- [ ] **抖音**: 视频上传、图文视频发布
- [ ] **Bilibili**: 视频投稿、分 P 管理
- [ ] **今日头条**: 视频内容同步

### Phase 4: 高级功能
- [ ] 多平台内容同步发布
- [ ] 内容自动适配（根据平台特点调整格式）
- [ ] 定时发布任务
- [ ] 发布数据统计

---

## 使用示例

### 发布微信公众号文章

```
用户: 帮我写一篇关于 AI 发展趋势的文章，并发布到微信公众号草稿箱

Claude:
1. 生成文章内容
2. 调用 wechat:push-draft skill
3. 返回文章链接和 mediaId
```

### 多平台同步发布

```
用户: 把这个内容同步发布到微博和小红书

Claude:
1. 根据各平台特点调整内容格式
   - 微博：添加话题标签，控制字数
   - 小红书：添加 emoji，优化排版
2. 调用 weibo:post 发布微博
3. 调用 xiaohongshu:post-note 发布笔记
4. 汇总各平台发布结果
```

### 批量管理

```
用户: 查看我所有平台的草稿箱

Claude:
1. 调用 wechat:get-drafts 获取微信草稿
2. 调用 weibo:get-drafts 获取微博草稿
3. 汇总展示所有草稿列表
```

---

## 开发规范

### Skill 命名规范

- **目录名**: `{platform-name}` (小写，连字符分隔)
- **Skill 名**: 与目录名一致
- **工具命名**: `{platform}:{action}` (平台前缀 + 动作)

### 代码组织

```javascript
// wechat-api.js

// 1. 配置和初始化
const WECHAT_API_BASE = 'https://api.weixin.qq.com';

// 2. 认证相关
async function getAccessToken() { ... }

// 3. 核心功能
async function pushDraft(title, content, options) { ... }
async function getDrafts(offset, count) { ... }
async function deleteDraft(mediaId) { ... }

// 4. 导出
module.exports = {
  pushDraft,
  getDrafts,
  deleteDraft
};
```

### 错误处理

- 所有 API 调用必须包含错误处理
- 返回统一的错误格式: `{ success: false, error: '错误信息' }`
- 成功返回格式: `{ success: true, data: {...} }`

---

## 环境变量配置

创建 `.env` 文件或在 `.claude/settings.local.json` 中配置：

```bash
# 微信公众号
WECHAT_APP_ID=your-app-id
WECHAT_APP_SECRET=your-app-secret

# 微博
WEIBO_API_KEY=your-api-key
WEIBO_API_SECRET=your-api-secret

# 小红书（需要 Cookie 或第三方 token）
XIAOHONGSHU_COOKIE=your-cookie

# 抖音
DOUYIN_CLIENT_KEY=your-client-key
DOUYIN_CLIENT_SECRET=your-client-secret

# Bilibili
BILIBILI_SESSDATA=your-sessdata
BILIBILI_CSRF=your-csrf

# 知乎
ZHIHU_COOKIE=your-cookie
```

---

## 技术实现方案

### 方案 A: 直接 API 调用
适合有官方开放 API 的平台：
- 微信公众号
- 微博
- 抖音（部分接口）

### 方案 B: 模拟登录 + 请求
适合有网页版管理后台的平台：
- 知乎
- Bilibili

### 方案 C: 浏览器自动化 (Playwright)
适合没有 API、反爬严格的平台：
- 小红书
- 部分需要复杂交互的平台

---

## 贡献指南

欢迎贡献新的平台 Skill！

### 提交新 Skill

1. 在 `skills/` 目录下创建平台目录
2. 编写 `skill.yaml` 定义 Skill 能力
3. 实现 API 调用逻辑
4. 更新 `Agent.md` 平台状态表
5. 提供使用示例

### Skill 审查清单

- [ ] `skill.yaml` 包含完整的 instructions
- [ ] 所有 tools 都有清晰的描述和参数说明
- [ ] API 实现包含错误处理
- [ ] 提供配置环境变量的说明
- [ ] 经过实际测试可用

---

## 相关资源

- [Claude Code Skills 文档](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/skills)
- [微信公众号 API 文档](https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Overview.html)
- [微博 API 文档](https://open.weibo.com/wiki/API)
- [抖音开放平台](https://open.douyin.com/platform)

---

## 许可证

MIT License

---

*Powered by Claude Code Skills*
