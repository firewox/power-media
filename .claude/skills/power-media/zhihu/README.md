# 知乎 (Zhihu) Skills

通过 computer-mcp 浏览器自动化操作知乎平台。

## 当前状态

| 技能 | 功能 | 状态 |
|------|------|------|
| `zhihu-check-login` | 检查登录状态 | ✅ 已完成 |
| `zhihu-publish-article` | 发布文章 | 🚧 开发中 |
| `zhihu-publish-answer` | 回答问题 | 📋 规划中 |
| `zhihu-publish-idea` | 发布想法 | 📋 规划中 |

## 技术方案

知乎无官方内容发布 API，采用 **computer-mcp** 浏览器自动化方案：
- 截图 + 多模态 AI 识别界面元素
- 鼠标/键盘模拟用户操作
- 复用系统浏览器登录态

详见 [SKILL.md](SKILL.md) 和 [技术方案](session-zhihu-plan.md)。
