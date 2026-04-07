# Power Media - AI 新媒体超级工具箱

## Skill 加载规则

**重要**: 本项目只使用项目本地 skills，不加载全局 skills。

- **忽略** `~/.config/opencode/skills/` 下的所有 skills
- **只从** `./.claude/skills/` 加载 skills

---

## 项目概述

Power Media 是一个基于 **Claude Code Skills** 构建的 AI 新媒体集成工具箱。通过构建自定义 Skills，让 AI 能够与多种主流新媒体平台进行交互，实现内容的自动化发布、管理和运营。

当前项目还集成了 `computer-mcp` 作为桌面执行层：AI 通过它对浏览器窗口进行截图识别，再通过鼠标点击、键盘输入和窗口控制来模拟人工操作，从而驱动媒体平台界面。

**核心设计理念**: 将每个新媒体平台的操作封装为可复用的 Skill，通过统一的接口调用，实现 AI 对多平台的无缝操作。

---

## 平台接入状态

| 平台 | Skill 名称 | 功能 | 状态 |
|------|-----------|------|------|
| 桌面执行层 | `computer-mcp` | 截图识别、鼠标点击、键盘输入、窗口控制 | ✅ 已完成 |
| 微信公众号 | `wechat` | 发布文章、素材管理、草稿管理 | ✅ 已完成 |
| 微博 | `weibo` | 发布微博、图文、获取时间线 | 🚧 开发中 |
| 小红书 | `xiaohongshu` | 发布图文/视频笔记 | 🚧 开发中 |
| 今日头条 | `toutiao` | 发布文章、微头条 | 📋 规划中 |
| 抖音 | `douyin` | 发布图文视频、管理作品 | 📋 规划中 |
| Bilibili | `bilibili` | 发布视频、动态 | 📋 规划中 |
| 知乎 | `zhihu` | 发布回答、文章、想法 | 📋 规划中 |

---

## 文档索引

| 文档 | 说明 |
|------|------|
| [项目架构](docs/architecture.md) | 整体架构、目录结构、技术方案 |
| [开发指南](docs/development-guide.md) | Skill 规范、命名规范、测试验收、Git 规范 |
| [环境配置](docs/environment-setup.md) | 各平台环境变量配置 |
| [开发路线图](docs/roadmap.md) | 开发计划和进度 |
| [使用示例](docs/usage-examples.md) | 各平台使用示例 |
| [相关资源](docs/resources.md) | 官方文档和平台入口 |
| [贡献指南](CONTRIBUTING.md) | 如何贡献新 Skill |

---

*Powered by Claude Code Skills*
