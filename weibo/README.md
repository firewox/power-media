# Weibo 微博 Skills

使用 computer-mcp 自动化操作桌面浏览器中的微博网页版。

## 前置要求

1. **系统环境**
   - Windows 10/11
   - Edge 或 Chrome 浏览器

2. **MCP 配置**
   确保 `.claude/settings.local.json` 中已配置：
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

3. **浏览器准备**
   - 打开浏览器
   - 访问 https://weibo.com
   - 保持窗口可见（不要最小化）

## Skills 列表

| Skill | 功能 | 触发词 |
|-------|------|--------|
| `weibo-check-login` | 检查登录状态 | "检查微博登录" |
| `weibo-login` | 扫码登录 | "登录微博" |
| `weibo-logout` | 退出登录 | "退出微博" |
| `weibo-post-text` | 发布纯文本微博 | "发微博" |
| `weibo-post-with-image` | 发布带图微博 | "发微博带图" |

## 使用流程

### 1. 首次使用

```
登录微博
```

AI 会：
1. 打开浏览器访问 weibo.com
2. 切换到扫码登录
3. 提示你使用手机 APP 扫码
4. 等待登录完成

### 2. 发布微博

```
发微博：今天天气真好！
```

AI 会：
1. 检查登录状态
2. 聚焦微博窗口
3. 点击输入框
4. 输入内容
5. 点击发送
6. 确认发布

### 3. 发布带图微博

```
发微博带图，文字是"测试图片"，图片是 C:\Users\xxx\Pictures\test.jpg
```

## 工作原理

这些 skills 使用 **computer-mcp** 进行桌面自动化：

1. **截图识别** - 使用 `inspect_screen` 获取界面文字和位置
2. **窗口管理** - 使用 `focus_window` 聚焦浏览器窗口
3. **模拟操作** - 使用 `click`, `type_text`, `hotkey` 模拟用户操作
4. **安全确认** - 使用 `confirm_action` 确保高风险操作需人工确认

不再使用 Playwright，无需维护 DOM 选择器，更加稳定可靠。

## 故障排查

### 找不到微博窗口
- 确保浏览器已打开
- 确保访问了 weibo.com
- 确保窗口标题包含"微博"

### OCR 识别失败
- 确保窗口未被其他窗口遮挡
- 尝试放大浏览器窗口
- 检查 computer-mcp 是否正常运行

### 点击位置不准确
- OCR 返回的是文字区域，点击位置可能有偏差
- 技能会自动调整偏移量
- 如持续失败，可手动操作后让 AI 继续

## 技术架构

```
用户请求
    ↓
Weibo Skill (SKILL.md 描述)
    ↓
computer-mcp (MCP Server)
    ├── screenshot / inspect_screen
    ├── focus_window
    ├── click / type_text / hotkey
    └── confirm_action
    ↓
桌面浏览器 (用户已打开的窗口)
```

## 迁移说明

本项目已从 Playwright 迁移到 computer-mcp：
- ❌ 不再使用 Node.js/Playwright 脚本
- ❌ 不再依赖 DOM 选择器
- ✅ 使用截图+OCR 识别界面
- ✅ 操作真实桌面浏览器窗口

## 相关文档

- [Agent 调用协议](../docs/AGENT-CALLING-PROTOCOL.md)
- [迁移技术规格](../docs/superpowers/specs/2026-04-11-weibo-computer-mcp-migration.md)
