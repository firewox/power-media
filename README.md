# Power Media - AI 新媒体超级工具箱

自动化操作多个主流新媒体平台（微信公众号、微博、小红书、知乎等），实现内容的自动发布、管理和运营。

## 核心特性

- **多平台支持**: 微信公众号、微博、小红书、知乎等主流平台
- **AI 驱动**: 多模态 AI 模型直接理解截图内容，智能定位界面元素
- **安全可靠**: 高风险操作人工确认，操作日志完整可追溯
- **可扩展**: 标准化 Skill 规范，轻松接入新平台

## 快速开始


## 平台状态

| 平台 | 状态 | 功能 |
|------|------|------|
| 微信公众号 | ✅ 已完成 | 发布文章、素材管理、草稿管理 |
| 微博 | 🚧 开发中 | 发布微博、图文、获取时间线 |
| 小红书 | 🚧 开发中 | 发布图文/视频笔记 |
| 知乎 | 📋 规划中 | 发布回答、文章、想法 |

## 架构

```
AI Agent (多模态模型)
    ↓ 截图分析 + 决策
Skills 层 (平台能力封装)
    ↓ 调用指令
computer-mcp (桌面执行层)
    ↓ 模拟操作
新媒体平台
```

## 技术栈

- **Python >= 3.13** / **uv** 包管理
- **mss** - 截图
- **pyautogui** - 鼠标/键盘模拟
- **ctypes** - Windows 窗口控制
- **MCP (Model Context Protocol)** - AI 工具调用协议

## 文档

- [项目架构](docs/architecture.md)
- [开发指南](docs/development-guide.md)
- [环境配置](docs/environment-setup.md)
- [Agent 调用协议](docs/AGENT-CALLING-PROTOCOL.md)
- [使用示例](docs/usage-examples.md)

## 许可证

MIT License
