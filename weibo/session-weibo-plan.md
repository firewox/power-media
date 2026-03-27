# Session Weibo Plan - AI发布微博功能实施方案

**创建时间**: 2026-03-26  
**文档类型**: 技术规划文档  
**状态**: 已完成初步研究，待实施  

---

## 1. 项目背景和目标

### 1.1 背景
Power Media 是一个基于 Claude Code Skills 构建的 AI 新媒体集成工具箱。本项目旨在为 Power Media 添加微博（Weibo）平台的内容发布能力，实现 AI 自动化发微博功能。

### 1.2 目标
- 实现通过 AI 自动发布微博（纯文本+图片）
- 支持 OAuth2 认证流程
- 提供统一的 Skill 接口供 Claude 调用
- 确保符合微博 API 的各项限制和规范

### 1.3 成功标准
- [ ] 成功发布纯文本微博
- [ ] 成功发布带图片的微博
- [ ] 正确处理 OAuth2 认证流程
- [ ] 完善的错误处理和限流管理

---

## 2. 技术架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Code Skill                     │
│                    (weibo/skill.yaml)                    │
└─────────────────────────┬───────────────────────────────┘
                          │ 调用
┌─────────────────────────▼───────────────────────────────┐
│                  weibo-api.js (Node.js)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   OAuth2     │  │  Text Post   │  │ Image Upload │  │
│  │   认证模块    │  │   文本发布    │  │   图片发布   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────┬───────────────────────────────┘
                          │ HTTPS
┌─────────────────────────▼───────────────────────────────┐
│              Weibo Open API (api.weibo.com)              │
└─────────────────────────────────────────────────────────┘
```

### 2.2 数据流

1. **用户请求** → Claude Skill 接收发微博指令
2. **内容生成** → AI 生成微博内容（文本+可选图片）
3. **认证检查** → 验证 Access Token 有效性
4. **API 调用** → 调用微博 API 发布内容
5. **结果返回** → 返回发布结果和微博链接

---

## 3. 核心API端点和约束

### 3.1 API 端点

| 功能 | 端点 | 方法 |
|------|------|------|
| **OAuth授权** | `https://api.weibo.com/oauth2/authorize` | GET |
| **获取Token** | `https://api.weibo.com/oauth2/access_token` | POST |
| **发布纯文本** | `https://api.weibo.com/2/statuses/update.json` | POST |
| **发布带图片** | `https://upload.api.weibo.com/2/statuses/upload.json` | POST |
| **查询限流状态** | `https://api.weibo.com/2/account/rate_limit_status.json` | GET |

### 3.2 技术约束

| 约束项 | 规格 |
|--------|------|
| **文本长度** | 140个中文字符（URL-encoded UTF-8） |
| **图片格式** | JPEG, GIF, PNG |
| **图片大小** | 单张最大5MB |
| **多图限制** | 最多9张（需预上传获取 pic_id） |
| **Token有效期** | 默认2小时（**无 refresh token**） |
| **发布频率** | 每小时最多30条 |
| **IP限流** | 每小时15,000请求 |

### 3.3 关键错误码

| 错误码 | 含义 | 处理策略 |
|--------|------|---------|
| `21301` | 认证失败 | 检查token有效性 |
| `21327` | Token过期 | 引导重新授权 |
| `20016` | 发布太频繁 | 实现指数退避 |
| `20017` | 重复内容 | 添加随机后缀或拒绝 |
| `20012` | 文本过长 | 截断或拒绝 |
| `10023` | 超出限流 | 暂停并告警 |

---

## 4. 推荐技术栈

### 4.1 核心依赖

| 组件 | 推荐方案 | 理由 |
|------|---------|------|
| **HTTP客户端** | `axios` (Node.js) | 支持 multipart/form-data，Promise-based |
| **OAuth库** | `simple-oauth2` 或原生实现 | 标准OAuth2实现 |
| **图片处理** | `sharp` | 格式转换、压缩、调整大小 |
| **表单数据** | `form-data` | 处理文件上传 |
| **配置管理** | `dotenv` | 环境变量管理 |

### 4.2 可选SDK

| SDK | 语言 | Stars | 状态 |
|-----|------|-------|------|
| `sinaweibopy` | Python | 1.3k | 官方推荐，已归档 |
| `lxyu/weibo` | Python | 234 | 现代，活跃 |
| `weibo-node-api` | Node.js | ~10 | TypeScript支持 |

**建议**: 由于 Node.js SDK 不够成熟，建议基于 `axios` 自行封装。

---

## 5. 实施步骤和时间规划

### Phase 1: 基础框架（1-2天）

- [ ] 创建 `weibo/skill.yaml` 定义 Skill 能力
- [ ] 实现 OAuth2 认证流程（authorize + access_token）
- [ ] 封装基础 HTTP 请求模块
- [ ] 添加统一错误处理机制
- [ ] 创建配置文件管理

### Phase 2: 核心功能（2-3天）

- [ ] 实现纯文本发布 API (`statuses/update`)
- [ ] 实现图片上传+发布 API (`statuses/upload`)
- [ ] 添加内容长度验证（140字符限制）
- [ ] 实现限流监控和检查
- [ ] 添加发布历史记录功能

### Phase 3: 高级功能（1-2天）

- [ ] 多图发布支持（需预上传图片获取 pic_id）
- [ ] 定时发布功能（可选）
- [ ] Token 过期提醒机制
- [ ] 发布统计和日志

### Phase 4: 测试优化（1天）

- [ ] 单元测试（认证、发布、错误处理）
- [ ] 错误场景测试（限流、token过期、内容违规）
- [ ] 文档完善和示例代码
- [ ] 代码审查和优化

**总计**: 5-8 天

---

## 6. 文件结构设计

```
.claude/skills/weibo/
├── skill.yaml              # Skill定义和指令
├── weibo-api.js            # 核心API实现（Node.js）
├── auth.js                 # OAuth2认证模块
├── config.js               # 配置管理
├── errors.js               # 错误定义和处理
├── utils.js                # 工具函数
├── package.json            # 依赖
└── README.md               # 使用说明

.env                        # 环境变量（不提交到git）
    WEIBO_APP_KEY=xxx
    WEIBO_APP_SECRET=xxx
    WEIBO_REDIRECT_URI=xxx
    WEIBO_ACCESS_TOKEN=xxx
```

---

## 7. 关键代码示例

### 7.1 OAuth2 认证流程

```javascript
// auth.js
const axios = require('axios');

const WEIBO_AUTH_URL = 'https://api.weibo.com/oauth2/authorize';
const WEIBO_TOKEN_URL = 'https://api.weibo.com/oauth2/access_token';

class WeiboAuth {
  constructor(appKey, appSecret, redirectUri) {
    this.appKey = appKey;
    this.appSecret = appSecret;
    this.redirectUri = redirectUri;
  }

  // 获取授权URL
  getAuthorizeUrl() {
    const params = new URLSearchParams({
      client_id: this.appKey,
      redirect_uri: this.redirectUri,
      response_type: 'code'
    });
    return `${WEIBO_AUTH_URL}?${params}`;
  }

  // 用code换取access_token
  async getAccessToken(code) {
    const response = await axios.post(WEIBO_TOKEN_URL, {
      client_id: this.appKey,
      client_secret: this.appSecret,
      grant_type: 'authorization_code',
      code,
      redirect_uri: this.redirectUri
    }, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    
    return {
      accessToken: response.data.access_token,
      expiresIn: response.data.expires_in,
      uid: response.data.uid
    };
  }
}

module.exports = WeiboAuth;
```

### 7.2 发布微博

```javascript
// weibo-api.js
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

class WeiboAPI {
  constructor(accessToken) {
    this.accessToken = accessToken;
    this.baseURL = 'https://api.weibo.com/2';
    this.uploadURL = 'https://upload.api.weibo.com/2';
  }

  // 发布纯文本微博
  async postText(status) {
    const url = `${this.baseURL}/statuses/update.json`;
    const response = await axios.post(url, {
      access_token: this.accessToken,
      status: encodeURIComponent(status)
    }, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return response.data;
  }

  // 发布带图片的微博
  async postWithImage(status, imagePath) {
    const url = `${this.uploadURL}/statuses/upload.json`;
    const form = new FormData();
    
    form.append('access_token', this.accessToken);
    form.append('status', encodeURIComponent(status));
    form.append('pic', fs.createReadStream(imagePath));

    const response = await axios.post(url, form, {
      headers: form.getHeaders()
    });
    return response.data;
  }

  // 检查限流状态
  async checkRateLimit() {
    const url = `${this.baseURL}/account/rate_limit_status.json`;
    const response = await axios.get(url, {
      params: { access_token: this.accessToken }
    });
    return response.data;
  }
}

module.exports = WeiboAPI;
```

### 7.3 Skill 定义示例

```yaml
# skill.yaml
name: weibo
version: 1.0.0
description: 微博内容发布和管理工具

instructions: |
  你有一个微博发布工具，可以执行以下操作：
  - 发布纯文本微博
  - 发布带图片的微博
  - 检查API限流状态
  
  当用户要求发布微博时：
  1. 生成或获取微博内容（注意140字限制）
  2. 如有图片，先下载或准备图片
  3. 调用 weibo:post 发布微博
  4. 返回发布结果和微博链接

tools:
  - name: weibo:post
    description: 发布微博
    args:
      - status: 微博内容（最多140个中文字符）
      - image_path: 图片路径（可选）
      
  - name: weibo:check-limit
    description: 检查API限流状态
    args: []

env:
  - WEIBO_APP_KEY: 微博应用App Key
  - WEIBO_APP_SECRET: 微博应用App Secret
  - WEIBO_REDIRECT_URI: OAuth回调地址
  - WEIBO_ACCESS_TOKEN: 访问令牌（通过OAuth获取）
```

---

## 8. 错误处理策略

### 8.1 错误分类

| 类别 | 错误类型 | 处理方式 |
|------|---------|---------|
| **认证错误** | Token过期、无效 | 提示用户重新授权 |
| **限流错误** | 超出频率限制 | 指数退避重试 |
| **内容错误** | 超长、重复、违规 | 前置验证，拒绝请求 |
| **网络错误** | 超时、连接失败 | 重试3次后报错 |

### 8.2 重试策略

```javascript
// 指数退避重试
async function retryWithBackoff(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (error.code === '10023' && i < maxRetries - 1) {
        const delay = Math.pow(2, i) * 1000; // 1s, 2s, 4s
        await sleep(delay);
        continue;
      }
      throw error;
    }
  }
}
```

---

## 9. 风险和注意事项

### 9.1 技术风险

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| **无Refresh Token** | 高 | Token过期需用户重新授权，建议设置提醒 |
| **严格的限流** | 中 | 实现限流检查，避免触发封禁 |
| **内容审核** | 中 | 添加敏感词过滤，避免违规内容 |
| **IP封禁** | 高 | 避免高频请求，实现智能轮询 |

### 9.2 合规风险

⚠️ **重要提醒：**

1. **实名认证**: 微博要求开发者实名认证，外国公司注册复杂
2. **内容合规**: 所有内容需符合中国法规和微博社区规范
3. **测试限制**: 未审核应用仅15个测试账号，token仅1天有效
4. **自动化风险**: 过度自动化可能触发反作弊机制

### 9.3 替代方案

如果官方API限制过多，可考虑：
- **TikHub.io**: 第三方API聚合服务
- **Playwright**: 浏览器自动化（风险较高，可能违反ToS）

---

## 10. 下一步行动计划

### 立即执行
- [ ] 1. 创建 `weibo/` 目录和基础文件结构
- [ ] 2. 编写 `skill.yaml` 定义文件
- [ ] 3. 实现 `auth.js` OAuth2 认证模块
- [ ] 4. 实现 `weibo-api.js` 核心API

### 短期目标（本周）
- [ ] 5. 完成纯文本发布功能
- [ ] 6. 完成图片发布功能
- [ ] 7. 添加基础错误处理

### 中期目标（下周）
- [ ] 8. 完善限流和重试机制
- [ ] 9. 编写测试用例
- [ ] 10. 编写使用文档

---

## 附录

### A. 参考资料

- [微博开放平台](https://open.weibo.com)
- [API文档 V2](https://open.weibo.com/wiki/API%E6%96%87%E6%A1%A3_V2/en)
- [OAuth2文档](https://open.weibo.com/wiki/Oauth/en)
- [sinaweibopy SDK](https://github.com/michaelliao/sinaweibopy)

### B. 环境变量模板

```bash
# .env
WEIBO_APP_KEY=your_16_char_app_key
WEIBO_APP_SECRET=your_app_secret
WEIBO_REDIRECT_URI=https://yourdomain.com/callback
WEIBO_ACCESS_TOKEN=obtained_after_oauth
```

### C. 变更日志

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-03-26 | v1.0 | 初始版本，完成技术调研和方案设计 |

---

*文档创建者: Claude Code*  
*最后更新: 2026-03-26*
