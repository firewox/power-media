# 开发指南

## Skill 定义规范

每个 Skill 由两部分组成：

### 1. skill.yaml - Skill 元数据和指令

```yaml
name: wechat-official-account
version: 1.0.0
description: 微信公众号内容发布和管理

instructions: |
  你有一个微信公众号管理工具，可以执行以下操作：
  - 发布文章到草稿箱
  - 获取草稿列表
  - 删除草稿
  - 上传图片素材

tools:
  - name: wechat:push-draft
    description: 推送文章到微信公众号草稿箱
    args:
      - title: 文章标题
      - content: 文章内容（支持 Markdown）
      - digest: 文章摘要（可选）
      - cover_image: 封面图片 URL（可选）

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

## Skill 命名规范

- **目录名**: `{platform-name}` (小写，连字符分隔)
- **Skill 名**: 与目录名一致
- **工具命名**: `{platform}:{action}` (平台前缀 + 动作)

---

## 代码组织

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

---

## 错误处理

- 所有 API 调用必须包含错误处理
- 返回统一的错误格式: `{ success: false, error: '错误信息' }`
- 成功返回格式: `{ success: true, data: {...} }`

---

## Skill 测试验收规范

### 测试流程

1. **执行测试**：运行 skill 并获取实际输出结果
2. **展示结果**：向用户展示完整的测试结果（输出内容、生成的文件等）
3. **等待验收**：由用户决定是否验收通过，**不要自行判定**
4. **更新状态**：用户确认验收后，再更新 session 文件中的状态

### 验收标准

- 功能是否符合预期
- 输出格式是否正确
- 边界条件是否处理
- 错误处理是否完善

### 禁止行为

❌ **不要**在未经用户确认的情况下自行判定 skill 测试通过  
❌ **不要**擅自删除测试生成的文件  
❌ **不要**自动更新验收状态
❌ **不要**省略测试结果 - 必须完整展示所有输出

---

## Git 提交规范

### 提交语言
**English**

### 提交格式
```
<Type>: <Description>
```

### 提交类型

| 类型 | 用途 |
|------|------|
| **Add** | 添加新功能、新文件 |
| **Fix** | 修复 bug |
| **Update** | 更新文档、配置 |
| **Remove** | 删除文件、功能 |
| **Modify** | 修改现有文件 |
| **Refactor** | 重构代码（不改变功能）|

### 示例

```
Add: Add user authentication feature
Fix: Fix login redirect bug
Update: Update README documentation
Remove: Remove deprecated API endpoints
Modify: Modify error handling logic
Refactor: Refactor database connection code
```
