# RedNote Skills 测试规范

> 本文档规定如何正确测试 RedNote Skills，避免常见错误

---

## 🚀 快速开始

```bash
# 1. 运行测试前检查
node test/pre-test-check.js

# 2. 按顺序运行测试
node test/run-all-tests.js
```

---

## 📋 测试前检查清单

### 环境检查
- [ ] Playwright 已安装: `npm list playwright`
- [ ] Firefox 浏览器已安装: `npx playwright install firefox`
- [ ] 网络可访问小红书: `curl -I https://www.xiaohongshu.com`

### 目录结构
- [ ] `data/` 目录存在
- [ ] `debug/` 目录存在（用于截图）
- [ ] 测试图片准备（用于 publish-note）

---

## 🔄 正确的测试顺序

### Phase 1: 环境验证
```bash
# 验证基础设施
node test/verify-environment.js
```

### Phase 2: 无需登录功能
```bash
# 1. 获取推荐列表（验证数据提取）
node get-feeds/scripts/get-feeds.js --count 5

# 2. 验证选择器（截图调试）
node test/validate-selectors.js
```

### Phase 3: 登录流程
```bash
# 1. 获取二维码（用户需要扫码）
node get-qrcode/scripts/get-qrcode.js

# 2. 验证登录状态
node check-login/scripts/check-login.js
```

### Phase 4: 需登录功能
```bash
# 使用真实 noteId 测试
node like/scripts/like.js --noteId "<真实ID>"

# 发布测试
node publish-note/scripts/publish-note.js \
  --title "测试标题" \
  --content "测试内容" \
  --images "test/image.jpg"
```

---

## ⚠️ 常见错误及避免方法

### 错误 1: 浏览器未安装
**症状**: `Executable doesn't exist at ... firefox.exe`

**避免**:
```bash
# 测试前运行
npx playwright install firefox
```

### 错误 2: 选择器失效
**症状**: `未找到 xxx 元素`

**避免**:
1. 先运行验证工具检查选择器
2. 查看截图确认页面结构
3. 使用多选择器策略

### 错误 3: 未登录就测试需登录功能
**症状**: 搜索返回 0 条结果，操作无权限

**避免**:
1. 查看 skill 文档确认是否需要登录
2. 先完成登录流程
3. 使用 check-login 验证状态

### 错误 4: 使用假数据测试
**症状**: `未找到点赞按钮`，笔记不存在

**避免**:
1. 从 get-feeds 获取真实 noteId
2. 使用测试数据管理工具

---

## 🧪 调试工具

### 1. 选择器验证工具
```bash
node test/validate-selectors.js --url "https://creator.xiaohongshu.com/"
```

### 2. 页面结构探测
```bash
node test/inspect-page.js --url "https://www.xiaohongshu.com/"
```

### 3. 截图对比
所有失败测试会自动保存截图到 `debug/` 目录

---

## 📊 测试报告规范

每次测试后应生成报告：

```markdown
## 测试报告: [Skill 名称]

### 环境
- Playwright: [版本]
- 浏览器: [类型+版本]
- 时间: [日期]

### 测试结果
| 功能 | 状态 | 备注 |
|------|------|------|
| xxx | ✅/❌ | 说明 |

### 问题记录
1. **问题**: [描述]
   - **原因**: [分析]
   - **解决**: [方案]

### 截图
[如有问题，附截图]
```

---

## 📝 提交规范

### 修复选择器时
```bash
# 1. 先验证新选择器
node test/validate-selectors.js

# 2. 运行完整测试
node test/run-all-tests.js

# 3. 提交时说明
Fix: 更新 xxx 选择器
- 原选择器: .old-selector
- 新选择器: .new-selector
- 测试: ✅ 通过
```

### 添加新技能时
```bash
# 1. 添加测试
node test/test-new-skill.js

# 2. 更新测试文档
# 3. 确保通过所有检查
```
