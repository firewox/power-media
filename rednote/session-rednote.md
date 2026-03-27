# RedNote (小红书) Skills 开发方案

> 创建时间: 2026-03-28
> 状态: 规划完成，待实现

---

## 一、项目概述

### 1.1 目标

为 Power Media 项目开发小红书（RedNote）平台的原子化 Tool Skills，实现 AI 自动化管理小红书账号，包括：

- 登录认证管理
- 图文/视频笔记发布
- 内容搜索与获取
- 用户互动（点赞、收藏、评论）

### 1.2 技术背景

**核心发现**：小红书官方开放平台 (`open.xiaohongshu.com`) 仅提供电商 API，**不提供内容发布 API**。

**解决方案**：借鉴开源项目 [xpzouying/xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) 的实现思路：

- 使用 Playwright 进行浏览器自动化
- 操作小红书创作者平台 `creator.xiaohongshu.com`
- 通过 CDP (Chrome DevTools Protocol) 控制浏览器
- Cookie 持久化保持登录状态

---

## 二、Skill 结构规范

### 2.1 目录结构

```
rednote/
├── check-login/                    # 独立 skill 目录
│   ├── SKILL.md                    # Skill 定义（AI 读取）
│   ├── usage.md                    # 使用说明（人类浏览）
│   └── scripts/
│       ├── check-login.js          # 实现脚本
│       └── install-deps.sh         # 依赖安装（可选）
├── get-qrcode/
│   ├── SKILL.md
│   ├── usage.md
│   └── scripts/
│       └── get-qrcode.js
├── ... (其他 skills)
├── lib/                            # 共享库（非 skill）
│   ├── browser.js                  # 浏览器管理
│   ├── cookie.js                   # Cookie 管理
│   └── utils.js                    # 工具函数
└── session-rednote.md              # 本文档
```

### 2.2 单个 Skill 文件说明

| 文件 | 用途 | 读取者 |
|------|------|--------|
| `SKILL.md` | Skill 定义、触发条件、工作流程 | AI (Claude) |
| `usage.md` | 详细使用说明、配置方法 | 人类用户 |
| `scripts/*.js` | 具体实现代码 | CLI / 模块调用 |
| `scripts/install-deps.sh` | 依赖安装脚本 | Shell |

### 2.3 SKILL.md 模板

```yaml
---
name: skill-name
description: |
  功能描述，触发条件说明。
  
  当用户说以下任何内容时触发此 skill：
  - "触发短语1"
  - "触发短语2"
  - 任何涉及XXX的请求

  此 skill 自动完成：
  - 功能1
  - 功能2

  使用前必须配置XXX。

compatibility: |
  - Node.js 环境
  - Playwright
  - 依赖：xxx
---

# Skill 标题

## 工作流程

1. 步骤1
2. 步骤2

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| param1 | string | 是 | 说明 |

## 输出结果

```json
{
  "success": true,
  "data": "..."
}
```

## 配置要求

环境变量：
- `XHS_COOKIE_PATH`: Cookie 存储路径

## 使用示例

```
用户：检查小红书登录状态
结果：已登录，用户名: xxx
```

## 注意事项

1. 注意事项1
2. 注意事项2
```

---

## 三、Tool Skills 开发计划

### 3.1 Phase 1: 基础设施 + 认证 ⚡ 最高优先级

| Tool Skill | 功能 | 借鉴源码 | 输入 | 输出 | 状态 |
|------------|------|----------|------|------|------|
| `lib/browser.js` | 浏览器管理 | - | - | Browser instance | 📋 待开发 |
| `lib/cookie.js` | Cookie 管理 | - | - | Cookie 数据 | 📋 待开发 |
| `lib/utils.js` | 工具函数 | - | - | - | 📋 待开发 |
| `check-login` | 检查登录状态 | `login.go` | - | `{ isLoggedIn, username }` | 📋 待开发 |
| `get-qrcode` | 获取登录二维码 | `login.go` | - | `{ qrcode_base64, deadline }` | 📋 待开发 |
| `logout` | 登出/清除登录 | `login.go` | - | `{ success }` | 📋 待开发 |

**借鉴源码位置**：`xiaohongshu-mcp/xiaohongshu/login.go`

### 3.2 Phase 2: 内容发布 🔥 高优先级

| Tool Skill | 功能 | 借鉴源码 | 输入 | 输出 | 状态 |
|------------|------|----------|------|------|------|
| `publish-note` | 发布图文笔记 | `publish.go` | `{ title, content, images[], tags[]?, visibility?, schedule_at?, is_original?, products[]? }` | `{ success, note_id }` | 📋 待开发 |
| `publish-video` | 发布视频笔记 | `publish_video.go` | `{ title, content, video, tags[]?, visibility?, schedule_at?, products[]? }` | `{ success, note_id }` | 📋 待开发 |

**借鉴源码位置**：
- `xiaohongshu-mcp/xiaohongshu/publish.go`
- `xiaohongshu-mcp/xiaohongshu/publish_video.go`

### 3.3 Phase 3: 内容获取 📈 中优先级

| Tool Skill | 功能 | 借鉴源码 | 输入 | 输出 | 状态 |
|------------|------|----------|------|------|------|
| `search` | 搜索内容 | `search.go` | `{ keyword, filters? }` | `{ feeds[] }` | 📋 待开发 |
| `get-feed` | 获取帖子详情 | `feed_detail.go` | `{ feed_id, xsec_token, load_comments? }` | `{ feed, comments[] }` | 📋 待开发 |
| `get-feeds` | 获取推荐列表 | `feeds.go` | - | `{ feeds[] }` | 📋 待开发 |
| `get-profile` | 获取用户主页 | `user_profile.go` | `{ user_id, xsec_token }` | `{ user, notes[] }` | 📋 待开发 |

**借鉴源码位置**：
- `xiaohongshu-mcp/xiaohongshu/search.go`
- `xiaohongshu-mcp/xiaohongshu/feed_detail.go`
- `xiaohongshu-mcp/xiaohongshu/feeds.go`
- `xiaohongshu-mcp/xiaohongshu/user_profile.go`

### 3.4 Phase 4: 互动功能 💬 标准优先级

| Tool Skill | 功能 | 借鉴源码 | 输入 | 输出 | 状态 |
|------------|------|----------|------|------|------|
| `like` | 点赞/取消点赞 | `like_favorite.go` | `{ feed_id, xsec_token, unlike? }` | `{ success }` | 📋 待开发 |
| `favorite` | 收藏/取消收藏 | `like_favorite.go` | `{ feed_id, xsec_token, unfavorite? }` | `{ success }` | 📋 待开发 |
| `comment` | 发表评论 | `comment_feed.go` | `{ feed_id, xsec_token, content }` | `{ success }` | 📋 待开发 |
| `reply` | 回复评论 | `comment_feed.go` | `{ feed_id, xsec_token, comment_id?, user_id?, content }` | `{ success }` | 📋 待开发 |

**借鉴源码位置**：
- `xiaohongshu-mcp/xiaohongshu/like_favorite.go`
- `xiaohongshu-mcp/xiaohongshu/comment_feed.go`

---

## 四、技术实现要点

### 4.1 核心依赖

```bash
# 安装 Playwright
npm install playwright

# 安装浏览器
npx playwright install chromium
```

### 4.2 浏览器自动化关键点

```javascript
// lib/browser.js 核心逻辑

const { chromium } = require('playwright');
const path = require('path');

class BrowserManager {
  constructor(cookiePath) {
    this.cookiePath = cookiePath;
    this.browser = null;
    this.context = null;
    this.page = null;
  }

  async launch() {
    // 启动浏览器（持久化上下文）
    this.context = await chromium.launchPersistentContext(
      path.join(this.cookiePath, 'browser-data'),
      {
        headless: false,  // 小红书需要非无头模式
        viewport: { width: 1280, height: 720 }
      }
    );
    this.page = this.context.pages()[0] || await this.context.newPage();
    return this.page;
  }

  async close() {
    await this.context?.close();
  }
}
```

### 4.3 登录流程

```
1. 用户调用 get-qrcode 获取登录二维码
2. 用户用小红书 App 扫码登录
3. 登录成功后 Cookie 自动保存到本地
4. 后续操作使用 check-login 验证登录状态
```

### 4.4 发布笔记流程

```
1. 检查登录状态
2. 导航到 creator.xiaohongshu.com/publish/publish
3. 点击"上传图文"或"上传视频"
4. 上传图片/视频
5. 填写标题、内容
6. 添加话题标签
7. 设置可见范围、定时发布等选项
8. 点击发布
```

---

## 五、关键 URL 和选择器

### 5.1 小红书平台 URL

| 页面 | URL |
|------|-----|
| 创作者中心 | `https://creator.xiaohongshu.com/` |
| 发布页面 | `https://creator.xiaohongshu.com/publish/publish?source=official` |
| 搜索页面 | `https://www.xiaohongshu.com/search_result?keyword={keyword}` |
| 用户主页 | `https://www.xiaohongshu.com/user/profile/{user_id}` |
| 笔记详情 | `https://www.xiaohongshu.com/explore/{feed_id}` |

### 5.2 关键选择器（来自 xiaohongshu-mcp）

```javascript
// 发布页面
const SELECTORS = {
  publishTab: 'div.creator-tab',
  uploadInput: '.upload-input',
  titleInput: 'div.d-input input',
  contentEditor: 'div.ql-editor',
  publishButton: '.publish-page-publish-btn button.bg-red',
  
  // 登录检测
  loginCheck: '.user-info',
  
  // 搜索
  searchInput: 'input.search-input',
  feedItem: '.note-item',
};
```

---

## 六、风险与限制

### 6.1 风险

| 风险 | 说明 | 缓解措施 |
|------|------|----------|
| 账号封禁 | 频繁自动操作可能触发风控 | 频率控制、随机延迟、模拟人类行为 |
| Cookie 过期 | 需要定期重新登录 | 登录状态检测、自动提醒 |
| 验证码 | 发布时可能触发滑块验证 | 人工介入处理 |
| 单设备登录限制 | 同账号只能单网页端登录 | 仅使用 MCP 服务端操作，避免其他网页登录 |

### 6.2 平台限制

- **标题长度**: 最多 20 个字
- **正文长度**: 最多 1000 个字
- **图片数量**: 最多 18 张
- **标签数量**: 最多 10 个
- **日发布量**: 约 50 篇

---

## 七、参考资源

### 7.1 开源项目

| 项目 | 地址 | 说明 |
|------|------|------|
| xiaohongshu-mcp | https://github.com/xpzouying/xiaohongshu-mcp | 主要参考，Go + Rod 实现 |
| x-mcp | https://github.com/xpzouying/x-mcp | 浏览器插件版本 |
| MediaCrawler | https://github.com/NanmiCoder/MediaCrawler | 小红书爬虫实现 |

### 7.2 xiaohongshu-mcp 源码文件对照

| 功能 | 源码文件 | 行数 |
|------|----------|------|
| 登录 | `xiaohongshu/login.go` | ~100 |
| 发布图文 | `xiaohongshu/publish.go` | ~800 |
| 发布视频 | `xiaohongshu/publish_video.go` | ~200 |
| 搜索 | `xiaohongshu/search.go` | ~250 |
| Feed 列表 | `xiaohongshu/feeds.go` | ~50 |
| Feed 详情 | `xiaohongshu/feed_detail.go` | ~600 |
| 点赞收藏 | `xiaohongshu/like_favorite.go` | ~200 |
| 评论 | `xiaohongshu/comment_feed.go` | ~250 |
| 用户主页 | `xiaohongshu/user_profile.go` | ~120 |

---

## 八、开发进度

### 状态说明

- 📋 待开发
- 🚧 开发中
- ✅ 已完成
- ❌ 已取消

### 开发进度统计

| 阶段 | Skills 数量 | 完成数 | 状态 |
|------|-------------|--------|------|
| Phase 1: 基础设施+认证 | 6 | 0 | 📋 待开发 |
| Phase 2: 内容发布 | 2 | 0 | 📋 待开发 |
| Phase 3: 内容获取 | 4 | 0 | 📋 待开发 |
| Phase 4: 互动功能 | 4 | 0 | 📋 待开发 |
| **总计** | **16** | **0** | - |

---

## 九、变更日志

| 日期 | 变更内容 |
|------|----------|
| 2026-03-28 | 创建文档，完成开发方案规划 |
| 2026-03-28 | 确定 Skill 结构规范（SKILL.md + usage.md + scripts/） |

---

## 十、下一步行动

1. **创建 lib/ 共享库**
   - `lib/browser.js` - 浏览器管理
   - `lib/cookie.js` - Cookie 管理
   - `lib/utils.js` - 工具函数

2. **实现 Phase 1 认证 Skills**
   - `check-login/` - 检查登录状态
   - `get-qrcode/` - 获取登录二维码
   - `logout/` - 登出

3. **测试验证**
   - 验证登录流程
   - 验证 Cookie 持久化

---

*本文档记录 RedNote (小红书) Skills 的开发方案和进度，用于跟踪和延续开发工作。*
