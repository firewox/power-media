# RedNote Skills 测试改进总结

> 针对测试过程中暴露的问题，提供系统性改进方案

---

## ❌ 测试中暴露的问题

### 问题清单

| # | 问题 | 症状 | 根本原因 |
|---|------|------|----------|
| 1 | 浏览器未安装 | `Executable doesn't exist` | 未检查环境就运行测试 |
| 2 | 选择器失效 | `未找到二维码元素` | 复制旧选择器，未验证时效性 |
| 3 | 未登录测试需登录功能 | 搜索返回 0 条 | 未分析业务逻辑，顺序混乱 |
| 4 | 使用假数据 | 点赞找不到按钮 | 未准备真实测试数据 |
| 5 | 调试信息不足 | 难以定位问题 | 缺乏截图和上下文 |

---

## ✅ 改进方案（已实施）

### 1. 测试前环境检查工具

**文件**: `test/pre-test-check.js`

```bash
# 运行检查
node test/pre-test-check.js
```

**功能**:
- ✅ 检查 Playwright 是否安装
- ✅ 检查 Firefox 浏览器是否安装
- ✅ 检查 data/ 目录
- ✅ 检查 debug/ 目录
- ✅ 检查 lib 模块
- ✅ 检查测试图片

**输出示例**:
```
🔍 RedNote Skills 测试前检查

============================================================
检查 playwright... ✅
   Playwright 1.58.2

检查 browser... ✅
   Firefox 浏览器已安装

检查 dataDir... ✅
   data/ 目录已存在

检查 debugDir... ✅
   debug/ 目录已存在

检查 libModules... ✅
   所有 lib 模块已就绪

检查 testImages... ⚠️
   test-data/ 中没有图片（publish-note 测试需要）
============================================================

⚠️ 检查通过，但有警告（非阻塞）
```

---

### 2. 选择器验证工具

**文件**: `test/validate-selectors.js`

```bash
# 验证选择器
node test/validate-selectors.js --url "https://creator.xiaohongshu.com/"
```

**功能**:
- 测试多个候选选择器
- 自动截图保存
- 提取页面 class 列表
- 输出有效选择器

**解决**: 选择器失效问题

---

### 3. 测试辅助工具

**文件**: `test/test-helper.js`

**功能**:
- `getValidNoteId()`: 从推荐列表获取真实 noteId
- `findElement()`: 多选择器查找元素
- `waitForElement()`: 等待元素出现
- `saveDebugScreenshot()`: 自动保存调试截图

**解决**: 
- 假数据问题 → 使用真实数据
- 调试困难 → 自动截图

---

### 4. 测试文档

**文件**: `TESTING.md`

**内容**:
- 测试前检查清单
- 正确的测试顺序
- 常见错误及避免方法
- 调试工具使用说明

---

## 🔄 正确的测试流程

### 改进前（错误）

```
随机挑选技能测试
  ├─ check-login ❌ (浏览器未安装)
  ├─ search ❌ (未登录)
  ├─ like ❌ (假数据)
  └─ get-qrcode ⚠️ (选择器失效)
```

### 改进后（正确）

```
Step 1: 环境检查
  └─ node test/pre-test-check.js ✅

Step 2: 选择器验证
  └─ node test/validate-selectors.js --url "xxx" ✅

Step 3: 无需登录功能
  ├─ get-feeds ✅ (验证数据提取)
  └─ 截图确认页面结构 ✅

Step 4: 登录流程
  ├─ get-qrcode ✅ (用户扫码)
  └─ check-login ✅ (验证状态)

Step 5: 需登录功能
  ├─ search ✅
  ├─ like ✅ (使用真实noteId)
  └─ publish-note ✅
```

---

## 🛡️ 防御性编程改进

### 改进前

```javascript
// 问题：单一选择器，无错误上下文
const qrcode = await page.$(SELECTORS.qrcode);
if (!qrcode) {
  throw new Error('未找到二维码');
}
```

### 改进后

```javascript
// 改进：多选择器 + 详细错误 + 自动截图
const SELECTORS = {
  qrcode: [
    '.qrcode-box img',
    '.login-qrcode img',
    '[class*="qr"] img',
    'canvas'
  ]
};

const element = await TestHelper.findElement(
  page, 
  SELECTORS.qrcode, 
  '二维码'
);

if (!element) {
  await TestHelper.saveDebugScreenshot(page, 'qrcode-fail');
  throw new Error(
    `未找到二维码\n` +
    `URL: ${page.url()}\n` +
    `尝试的选择器: ${SELECTORS.qrcode.join(', ')}\n` +
    `截图: debug/qrcode-fail-{timestamp}.png`
  );
}
```

---

## 📊 测试数据管理

### 改进前
```bash
# 使用假数据
node like/scripts/like.js --noteId "abc123"
# ❌ 未找到点赞按钮
```

### 改进后
```javascript
// 自动获取真实数据
const noteId = await TestHelper.getValidNoteId();
// ✅ 使用从 get-feeds 获取的真实 noteId
```

---

## 🎯 关键改进点总结

| 改进项 | 解决的问题 | 文件 |
|--------|-----------|------|
| 环境检查 | 浏览器未安装 | `test/pre-test-check.js` |
| 选择器验证 | 选择器失效 | `test/validate-selectors.js` |
| 多选择器策略 | 单一选择器容错低 | `test/test-helper.js` |
| 自动截图 | 调试困难 | `test/test-helper.js` |
| 真实数据 | 假数据测试 | `test/test-helper.js` |
| 测试文档 | 流程混乱 | `TESTING.md` |

---

## 🚀 使用改进后的流程

```bash
# 1. 检查环境
node test/pre-test-check.js

# 2. 验证选择器
node test/validate-selectors.js --url "https://creator.xiaohongshu.com/"

# 3. 测试无需登录功能
node get-feeds/scripts/get-feeds.js --count 5

# 4. 登录（如需）
node get-qrcode/scripts/get-qrcode.js

# 5. 测试需登录功能
node search/scripts/search.js --keyword "旅游"
```

---

## 📈 预期效果

| 指标 | 改进前 | 改进后 |
|------|--------|--------|
| 环境错误 | 高 | 低（预检查） |
| 选择器失效 | 高 | 低（验证工具） |
| 调试时间 | 长 | 短（自动截图） |
| 测试数据 | 假 | 真（自动获取） |
| 测试顺序 | 混乱 | 清晰（文档） |

---

## 📝 后续建议

1. **定期运行选择器验证**（每周一次）
2. **建立 CI/CD 流程**自动化测试
3. **监控小红书页面变化**自动告警
4. **维护选择器映射表**记录版本对应关系

---

*改进完成时间: 2026-03-28*
