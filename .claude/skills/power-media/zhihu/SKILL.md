---
name: zhihu
description: |
  知乎内容管理自动化。

  当用户说以下任何内容时触发此 skill：
  - "发知乎文章"
  - "回答知乎问题"
  - "检查知乎登录状态"
  - "发布知乎想法"
  - "操作知乎"
  - 任何涉及知乎内容发布的请求

  此 skill 自动完成：
  - 检查登录状态
  - 发布文章到知乎专栏
  - 回答知乎问题
  - 发布想法
  - 图片上传

  注意：知乎没有官方内容发布 API，所有操作通过 computer-mcp 浏览器自动化完成。
  需确保浏览器已登录 zhihu.com。

compatibility: |
  - Windows 10/11
  - Python 3.8+
  - computer-mcp 服务器
  - 浏览器：Edge / Chrome / Firefox（已登录 zhihu.com）
---

# 知乎 (Zhihu) Skills

通过 computer-mcp 控制浏览器完成知乎操作。

## 前置要求

1. **系统环境**
   - Windows 10/11
   - Edge / Chrome / Firefox 浏览器
   - Python 3.8+

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

3. **登录准备**
   - 在浏览器中访问 https://www.zhihu.com 并登录
   - 脚本会复用浏览器的登录状态

## Skills 列表

| Skill | 功能 | 状态 |
|-------|------|------|
| `zhihu-check-login` | 检查知乎登录状态 | ✅ |
| `zhihu-publish-article` | 发布文章到知乎专栏 | 🚧 |
| `zhihu-publish-answer` | 回答知乎问题 | 📋 |
| `zhihu-publish-idea` | 发布想法 | 📋 |

## 检查登录状态

### 工作流程

1. 调用 computer-mcp `focus_window` 聚焦浏览器窗口
2. 导航到 `https://www.zhihu.com`
3. 调用 computer-mcp `screenshot` 截图
4. 多模态 AI 直接分析截图判断是否已登录
5. 返回登录状态

### 判断依据

| 特征 | 已登录 | 未登录 |
|------|--------|--------|
| 右上角头像 | 显示用户头像 | 显示"登录"按钮 |
| 首页顶部 | 显示用户昵称 | 显示登录/注册入口 |
| 创作中心入口 | 可见 | 不可见或提示登录 |

### 输出结果

```json
{
  "loggedIn": true,
  "userName": "用户名 (如果可见)",
  "message": "已登录知乎"
}
```

## 发布文章（开发中）

### 计划实现流程

1. 检查登录状态
2. 导航到 `https://zhuanlan.zhihu.com/write`
3. 截图识别发布页面元素
4. 填写标题和内容
5. 选择话题标签
6. 点击发布按钮
7. 确认发布结果

### 技术方案

详见 [session-zhihu-plan.md](session-zhihu-plan.md)

## 注意事项

1. **登录状态**: 依赖系统浏览器的知乎登录态
2. **窗口状态**: 确保知乎页面已打开且未被最小化
3. **频率控制**: 建议单账号日发布 ≤ 3 篇，发布间隔 30 秒以上
4. **安全确认**: 所有发布操作需要人工确认
5. **风控风险**: 频繁自动操作可能触发知乎风控机制

## 相关文档

- [知乎技术方案](session-zhihu-plan.md)
- [agent 调用协议](session-zhihu-plan.md#%E5%9B%9B%E6%8E%A8%E8%8D%90%E6%96%B9%E6%A1%88)
