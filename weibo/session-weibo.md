# Weibo Skills - Playwright 浏览器自动化方案

**创建时间**: 2026-03-28  
**文档类型**: 技术实现文档  
**状态**: ✅ 已完成  
**技术栈**: Node.js + Playwright

---

## 1. 项目概述

### 1.1 方案变更

原方案使用微博开放平台 API，后改为 **Playwright 浏览器自动化方案**。

**变更原因**:
- 避免 API Token 2 小时过期问题
- 绕过 API 限流限制（30条/小时）
- 更接近真实用户操作，降低被封风险
- 无需申请开发者资质

### 1.2 新方案优势

| 对比项 | API 方案 | Playwright 方案 |
|--------|----------|-----------------|
| 认证方式 | OAuth2 Token | Cookie/扫码登录 |
| Token 有效期 | 2 小时 | 持久（数天到数周） |
| 发布限流 | 30条/小时 | 接近真实用户 |
| 开发资质 | 需要 | 不需要 |
| 稳定性 | 依赖 API | 依赖 UI |

---

## 2. 技术架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Code Skills                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │  login   │ │  logout  │ │post-text │ │post-img  │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                   lib/weibo.js (共享库)                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ 浏览器启动 │ │  Cookie  │ │ 扫码等待  │ │ 发布操作  │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
└─────────────────────────┬───────────────────────────────┘
                          │ CDP / Playwright
┌─────────────────────────▼───────────────────────────────┐
│              Chromium Browser (Playwright)               │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                   weibo.com (网页版)                      │
└─────────────────────────────────────────────────────────┘
```

### 2.2 数据流

1. **login**: 打开浏览器 → 显示二维码 → 用户扫码 → 保存 Cookie
2. **check-login**: 加载 Cookie → 访问微博 → 检查登录元素
3. **post-text**: 加载 Cookie → 打开发布页 → 填写内容 → 点击发送
4. **post-with-image**: 加载 Cookie → 打开发布页 → 上传图片 → 填写内容 → 发送
5. **logout**: 删除 Cookie 文件

---

## 3. Skills 列表

### 3.1 已实现 Skills

| Skill | 功能 | 触发词 | 状态 |
|-------|------|--------|------|
| **check-login** | 检查登录状态 | "检查微博登录" | ✅ |
| **login** | 扫码登录 | "登录微博" | ✅ |
| **logout** | 退出登录 | "退出微博" | ✅ |
| **post-text** | 发布纯文本 | "发微博" | ✅ |
| **post-with-image** | 发布带图微博 | "发带图微博" | ✅ |

### 3.2 文件结构

```
weibo/
├── package.json              # 项目依赖
├── lib/
│   └── weibo.js             # 共享库（浏览器、Cookie、发布）
├── check-login/
│   ├── SKILL.md             # Skill 定义
│   ├── usage.md             # 使用说明
│   └── scripts/
│       └── check-login.js   # 检查脚本
├── login/
│   ├── SKILL.md
│   ├── usage.md
│   └── scripts/
│       └── login.js         # 登录脚本
├── logout/
│   ├── SKILL.md
│   ├── usage.md
│   └── scripts/
│       └── logout.js        # 登出脚本
├── post-text/
│   ├── SKILL.md
│   ├── usage.md
│   └── scripts/
│       └── post-text.js     # 发布文本脚本
└── post-with-image/
    ├── SKILL.md
    ├── usage.md
    └── scripts/
        └── post-with-image.js  # 发布带图脚本
```

---

## 4. 使用指南

### 4.1 安装依赖

```bash
cd /mnt/d/08_tmp/02_media/power-media/weibo
npm install
npx playwright install chromium
```

### 4.2 使用流程

```bash
# 1. 登录
node login/scripts/login.js
# 显示二维码，用手机微博 APP 扫描

# 2. 检查登录状态
node check-login/scripts/check-login.js

# 3. 发布纯文本微博
node post-text/scripts/post-text.js "Hello Weibo!"

# 4. 发布带图片的微博
node post-with-image/scripts/post-with-image.js "分享美景" "./photo.jpg"

# 5. 退出登录（删除 Cookie）
node logout/scripts/logout.js
```

### 4.3 Cookie 管理

- **存储位置**: `weibo/.cookies.json`
- **有效期**: 通常数天到数周
- **安全性**: 本地存储，不传输到远程

---

## 5. 核心实现

### 5.1 共享库 (lib/weibo.js)

| 函数 | 功能 |
|------|------|
| `launchBrowser()` | 启动 Chromium 浏览器 |
| `createContext()` | 创建浏览器上下文，加载 Cookie |
| `saveCookies()` | 保存 Cookie 到文件 |
| `clearCookies()` | 清除 Cookie 文件 |
| `checkLoginStatus()` | 检查登录状态 |
| `waitForQRCodeScan()` | 等待扫码完成 |
| `postText()` | 发布纯文本微博 |
| `postWithImage()` | 发布带图片微博 |

### 5.2 反检测措施

```javascript
// 禁用自动化标记
args: ['--disable-blink-features=AutomationControlled']

// 设置真实 UA
userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...'

// 设置视口
viewport: { width: 1920, height: 1080 }
```

---

## 6. 注意事项

### 6.1 限制

1. **需要图形界面**: login skill 需要显示浏览器
2. **Cookie 过期**: 需要定期重新登录
3. **UI 变化**: 微博页面改版可能导致脚本失效
4. **频率控制**: 避免过于频繁的自动化操作

### 6.2 风险

- 微博可能检测自动化行为
- 频繁操作可能触发验证码
- 建议控制发布频率（模拟人工）

### 6.3 最佳实践

- 发布间隔建议 30 秒以上
- 内容避免完全相同（防重复检测）
- 定期更新 Playwright 和浏览器

---

## 7. 维护记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-03-26 | v1.0 | API 方案（已废弃）|
| 2026-03-28 | v2.0 | Playwright 方案（当前）|

---

## 8. 参考资料

- [Playwright 文档](https://playwright.dev/)
- [微博网页版](https://weibo.com)

---

*文档创建者: Claude Code*  
*最后更新: 2026-03-28*
