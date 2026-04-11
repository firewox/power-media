# Weibo Skills 迁移至 computer-mcp 技术规格书

**日期**: 2026-04-11  
**作者**: Claude  
**状态**: 草稿 / 待评审

---

## 1. 背景与目标

### 1.1 背景
当前 Weibo skills 使用 **Playwright** 进行浏览器自动化，存在以下问题：
- 依赖特定 DOM 结构，易失效
- 需要维护独立的浏览器实例
- 与 `computer-mcp` 能力重复
- 不符合 `power-media` Desktop-First 架构设计

### 1.2 目标
将 Weibo skills 从 **Playwright Browser 模式** 迁移到 **computer-mcp Desktop 模式**：
- 通过截图 + OCR 识别界面元素
- 使用 `computer-mcp` 工具控制鼠标、键盘操作浏览器
- 统一使用桌面已打开的浏览器窗口
- 降低维护成本，提升稳定性

### 1.3 非目标
- 不修改 `computer-mcp` 本身的实现
- 不改变 skill 的对外接口（保持向后兼容）
- 不直接操作微博 API（仍使用网页版）

---

## 2. 架构变化

### 2.1 当前架构（Playwright）
```
User Request
    ↓
Weibo Skill (Node.js)
    ↓
Playwright → Launch Browser → DOM Operation → Return Result
```

### 2.2 目标架构（computer-mcp）
```
User Request
    ↓
Weibo Skill (Python / Skill Logic)
    ↓
computer-mcp (MCP Server)
    ├── screenshot / inspect_screen  (感知)
    ├── focus_window                 (窗口管理)
    ├── click / type_text / hotkey   (执行)
    └── confirm_action             (安全确认)
    ↓
Desktop Browser (用户已打开的窗口)
```

---

## 3. Skill 迁移详单

### 3.1 check-login → weibo-check-login
**功能**: 检查微博登录状态

**迁移方案**:
| 步骤 | 动作 | computer-mcp 工具 |
|------|------|------------------|
| 1 | 聚焦微博浏览器窗口 | `focus_window("weibo")` |
| 2 | 截取当前页面 | `screenshot()` |
| 3 | OCR 识别 | `inspect_screen()` |
| 4 | 分析 OCR 结果 | Skill 逻辑：检查是否有用户名/登录按钮 |
| 5 | 返回结果 | `{"loggedIn": true/false, "userName": "xxx"}` |

**识别逻辑**:
- 检测到 "登录" / "注册" 按钮 → 未登录
- 检测到用户名（如 "xxx 的微博"）→ 已登录
- 页面 URL 包含 `/u/` 且显示用户内容 → 已登录

---

### 3.2 login → weibo-login
**功能**: 扫码登录微博

**迁移方案**:
| 步骤 | 动作 | computer-mcp 工具 |
|------|------|------------------|
| 1 | 聚焦/打开浏览器 | `focus_window("Edge")` 或提示用户打开 |
| 2 | 访问微博登录页 | `hotkey("ctrl l")` → `type_text("weibo.com")` → `press_key("enter")` |
| 3 | 切换到扫码登录 | `inspect_screen()` → OCR 找 "扫码登录" → `click(x, y)` |
| 4 | 等待用户扫码 | `wait(3)` 循环检查登录状态 |
| 5 | 确认登录成功 | `inspect_screen()` 检测用户名 |
| 6 | 返回结果 | `{"success": true, "userName": "xxx"}` |

**安全注意**:
- 二维码有效期约 2 分钟，超时需刷新
- 无需保存 Cookie（依赖浏览器自身会话）

---

### 3.3 logout → weibo-logout
**功能**: 退出微博登录

**迁移方案**:
| 步骤 | 动作 | computer-mcp 工具 |
|------|------|------------------|
| 1 | 聚焦微博窗口 | `focus_window("weibo")` |
| 2 | 点击用户头像/菜单 | `inspect_screen()` 找 "设置"/头像 → `click(x, y)` |
| 3 | 点击退出登录 | `inspect_screen()` 找 "退出" → `click(x, y)` |
| 4 | 确认退出 | `confirm_action("确认退出微博登录？")` |
| 5 | 验证结果 | `inspect_screen()` 检查是否回到登录页 |

---

### 3.4 post-text → weibo-post-text
**功能**: 发布纯文本微博

**迁移方案**:
| 步骤 | 动作 | computer-mcp 工具 |
|------|------|------------------|
| 1 | 前置检查 | 调用 `weibo-check-login` 确认已登录 |
| 2 | 聚焦微博窗口 | `focus_window("weibo")` |
| 3 | 找到输入框 | `inspect_screen()` 找 "有什么新鲜事想告诉大家" |
| 4 | 点击输入框 | `click(x, y)` |
| 5 | 输入内容 | `type_text("用户输入的文本")` |
| 6 | 点击发送 | `inspect_screen()` 找 "发送" 按钮 → `click(x, y)` |
| 7 | 确认发布 | `confirm_action("确认发布微博？")` |
| 8 | 验证结果 | `inspect_screen()` 检查 "发布成功" 提示 |

**内容校验**:
- 文本长度 ≤ 140 字符（skill 层校验）
- 敏感词过滤（微博自身处理）

---

### 3.5 post-with-image → weibo-post-with-image
**功能**: 发布带图片的微博

**迁移方案**:
| 步骤 | 动作 | computer-mcp 工具 |
|------|------|------------------|
| 1 | 前置检查 | 调用 `weibo-check-login` + 校验图片存在 |
| 2 | 聚焦微博窗口 | `focus_window("weibo")` |
| 3 | 找到输入框 | `inspect_screen()` → `click(x, y)` |
| 4 | 输入文字 | `type_text("文本内容")` |
| 5 | 点击添加图片 | `inspect_screen()` 找 "图片" 图标/按钮 → `click(x, y)` |
| 6 | 选择图片文件 | `type_text("图片路径")` → `press_key("enter")` |
| 7 | 等待上传 | `wait(3)` + 循环 `inspect_screen()` 检查上传进度 |
| 8 | 点击发送 | `inspect_screen()` 找 "发送" → `click(x, y)` |
| 9 | 确认发布 | `confirm_action("确认发布带图微博？")` |
| 10 | 验证结果 | `inspect_screen()` 检查成功提示 |

**图片处理**:
- 格式：JPG, PNG, GIF
- 大小：建议 ≤ 5MB
- 数量：单条微博最多 18 张（本 skill 限制为 1-9 张）

---

## 4. 目录结构调整

### 4.1 当前结构
```
weibo/
├── check-login/
│   ├── SKILL.md
│   └── scripts/
│       └── check-login.js      # Node.js + Playwright
├── login/
│   ├── SKILL.md
│   └── scripts/
│       └── login.js
├── logout/
├── post-text/
├── post-with-image/
└── lib/
    └── weibo.js               # Playwright 公共库
```

### 4.2 目标结构
```
weibo/
├── README.md                   # 平台使用指南
├── SKILL.md                    # 平台级 skill 定义（可选）
│
├── check-login/
│   └── SKILL.md                # 更新：使用 computer-mcp
├── login/
│   └── SKILL.md
├── logout/
│   └── SKILL.md
├── post-text/
│   └── SKILL.md
├── post-with-image/
│   └── SKILL.md
│
└── lib/                        # 可选：保留工具函数
    └── utils.py                # 公共工具（如 OCR 结果解析）
```

**变化说明**:
- 移除所有 `scripts/` 目录（不再需要 Node.js 脚本）
- SKILL.md 更新为描述基于 computer-mcp 的工作流程
- 不再依赖 `weibo/lib/weibo.js`，改用 skill 直接调用 MCP 工具

---

## 5. Skill 定义模板

每个 skill 的 SKILL.md 应遵循以下模板：

```yaml
---
name: weibo-post-text
description: |
  使用 computer-mcp 发布纯文本微博。
  
  触发条件：
  - "发微博"
  - "发布微博"
  - "post weibo"
  
  工作流程：
  1. 调用 computer-mcp/focus_window 聚焦微博窗口
  2. 调用 computer-mcp/inspect_screen 识别界面元素
  3. 调用 computer-mcp/click 点击输入框
  4. 调用 computer-mcp/type_text 输入内容
  5. 调用 computer-mcp/click 点击发送
  6. 调用 computer-mcp/confirm_action 确认发布
  
  依赖：
  - computer-mcp (screenshot, inspect_screen, click, type_text, confirm_action)
  - 已登录的微博浏览器窗口

compatibility:
  - computer-mcp >= 1.0
  - Windows 10/11
  - Edge / Chrome 浏览器
---

# 发布纯文本微博

## 工作流程（computer-mcp）

### Step 1: 检查登录状态
调用 `weibo-check-login` 确认已登录。

### Step 2: 聚焦窗口
```json
{
  "tool": "computer-mcp/focus_window",
  "params": {"title": "微博"}
}
```

### Step 3: 识别输入框
```json
{
  "tool": "computer-mcp/inspect_screen",
  "params": {}
}
```
从 OCR 结果中定位 "有什么新鲜事想告诉大家" 的坐标。

### Step 4: 点击输入框
```json
{
  "tool": "computer-mcp/click",
  "params": {"x": <detected_x>, "y": <detected_y>}
}
```

### Step 5: 输入内容
```json
{
  "tool": "computer-mcp/type_text",
  "params": {"text": "{{content}}"}
}
```

### Step 6: 点击发送
从 OCR 结果中找到 "发送" 按钮坐标并点击。

### Step 7: 确认发布
```json
{
  "tool": "computer-mcp/confirm_action",
  "params": {"action_description": "确认发布微博？"}
}
```

### Step 8: 验证结果
再次调用 `inspect_screen` 检查是否有 "发布成功" 提示。

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| text | string | 是 | 微博内容，最多 140 字符 |

## 输出结果

```json
{
  "success": true,
  "message": "发布成功",
  "url": "https://weibo.com/xxx/xxx"
}
```

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 未登录 | 返回错误，提示先执行 weibo-login |
| 找不到输入框 | 重试截图，或提示用户检查页面 |
| 发送失败 | 返回错误信息 |
| 内容超长 | Skill 层校验，拒绝执行 |

## 注意事项

1. 必须先打开浏览器并访问 weibo.com
2. 确保微博窗口未被最小化
3. 内容长度限制 140 字符
4. 高风险操作需人工确认
```

---

## 6. 关键技术问题

### 6.1 OCR 准确性
**问题**: OCR 可能无法 100% 准确识别按钮文字  
**解决方案**:
- 使用图像匹配（OpenCV template matching）辅助定位
- 支持模糊匹配（如 "发" 匹配 "发送"）
- 允许用户通过 `computer-mcp` 手动点击作为 fallback

### 6.2 窗口识别
**问题**: 多个浏览器标签页，如何准确聚焦微博页面  
**解决方案**:
- `focus_window` 支持模糊匹配（如 "weibo", "微博"）
- 若未找到，提示用户手动切换到微博页面

### 6.3 页面加载等待
**问题**: 点击后页面可能正在加载  
**解决方案**:
- 每次操作后调用 `wait(1-2)`
- 循环 `inspect_screen` 检查目标元素是否出现
- 设置最大等待时间（如 10 秒），超时则报错

### 6.4 动态内容识别
**问题**: 微博页面元素位置可能随窗口大小变化  
**解决方案**:
- 不硬编码坐标，每次都重新 `inspect_screen`
- 使用相对位置（如 "在输入框右侧"）

---

## 7. 依赖与配置

### 7.1 必需依赖
- `computer-mcp` 已安装并运行
- Windows 10/11 系统
- Edge 或 Chrome 浏览器
- 浏览器中已打开 weibo.com 页面

### 7.2 MCP 配置
在 `.claude/settings.local.json` 中确保：
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

---

## 8. 验收标准

### 8.1 功能验收
- [ ] `weibo-check-login` 能正确识别登录状态
- [ ] `weibo-login` 能完成扫码登录流程
- [ ] `weibo-logout` 能成功退出登录
- [ ] `weibo-post-text` 能发布纯文本微博
- [ ] `weibo-post-with-image` 能发布带图微博

### 8.2 稳定性验收
- [ ] 连续执行 5 次发布操作，成功率 ≥ 80%
- [ ] 登录状态检查响应时间 ≤ 5 秒
- [ ] 发布操作总耗时 ≤ 30 秒

### 8.3 安全验收
- [ ] 所有发布操作都经过 `confirm_action` 确认
- [ ] 敏感操作有明确日志记录
- [ ] 错误时有清晰的提示信息

---

## 9. 迁移计划

### Phase 1: 基础 Skill（Week 1）
- [ ] 迁移 `weibo-check-login`
- [ ] 迁移 `weibo-login`
- [ ] 编写测试用例

### Phase 2: 发布 Skill（Week 2）
- [ ] 迁移 `weibo-post-text`
- [ ] 迁移 `weibo-post-with-image`
- [ ] 完善错误处理

### Phase 3: 清理与文档（Week 3）
- [ ] 迁移 `weibo-logout`
- [ ] 删除旧 Playwright 代码
- [ ] 更新 README 和文档
- [ ] 集成测试

---

## 10. 风险评估

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|---------|
| OCR 识别率不足 | 中 | 高 | 增加图像匹配、模糊匹配、人工 fallback |
| 微博页面改版 | 中 | 高 | 定期检查 OCR 关键词，建立监控 |
| 窗口焦点丢失 | 低 | 中 | 每次操作前重新 focus_window |
| 操作超时 | 低 | 低 | 设置合理超时时间，友好错误提示 |

---

## 附录

### A. OCR 关键词映射表

| 界面元素 | 可能的关键词 | 匹配策略 |
|---------|-------------|---------|
| 登录按钮 | "登录", "Login", "立即登录" | 模糊匹配 |
| 扫码登录 | "扫码", "二维码", "QR" | 精确匹配 |
| 输入框提示 | "有什么新鲜事", "说点什么" | 前缀匹配 |
| 发送按钮 | "发送", "发布", "Post" | 模糊匹配 |
| 添加图片 | "图片", "照片", "Image" | 模糊匹配 |
| 成功提示 | "发布成功", "发送成功" | 精确匹配 |
| 用户名显示 | "的微博" | 后缀匹配 |

### B. 坐标容错策略

由于 OCR 返回的是文本块的坐标，实际点击位置应进行微调：
- 按钮点击：文本中心点 + (0, 5) 像素
- 输入框点击：文本中心点（或上方 10 像素，避开光标）
- 图标点击：通过图像匹配获取精确坐标

---

**评审记录**

| 日期 | 评审人 | 意见 | 状态 |
|------|--------|------|------|
| 2026-04-11 | - | 初稿创建 | 📝 Draft |
