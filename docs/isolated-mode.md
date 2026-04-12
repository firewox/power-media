# 隔离模式 (Isolated Mode) 使用指南

## 概述

隔离模式通过 Windows 虚拟桌面技术,实现 AI 操作与用户工作的完全并行隔离。

**核心特性**:
- ✅ 完全并行隔离,AI 操作不影响用户
- ✅ 复用浏览器登录态 (Cookie/Session 共享)
- ✅ 用户完全无感知 (AI 在虚拟桌面 2 操作)
- ✅ 自动桌面切换,所有工具透明处理

---

## 系统要求

- Windows 10 1703+ 或 Windows 11
- Python 3.10+
- Chrome 或 Edge 浏览器
- 管理员权限 (推荐)

---

## 安装

```bash
cd isolated-mcp
pip install -r requirements.txt
```

---

## 配置

在 `.claude/settings.local.json` 中添加:

```json
{
  "mcpServers": {
    "isolated-computer": {
      "command": "python",
      "args": ["isolated-mcp/server.py"]
    }
  }
}
```

---

## 使用流程

### 1. 初始化隔离环境

```python
# 初始化 (可选 URL)
result = await mcp.tool_init_isolated("https://weibo.com")
# 返回: {"success": True, "desktop_id": "...", "window_hwnd": 12345}
```

### 2. 执行操作

所有操作自动处理虚拟桌面切换:

```python
# 截图
screenshot = await mcp.tool_screenshot()

# 获取浏览器窗口位置 (用于坐标映射)
rect = await mcp.tool_get_browser_rect()
# 返回: {"success": True, "left": 100, "top": 50, "width": 1200, "height": 800}

# 点击/输入等操作
await mcp.tool_click(x, y)
await mcp.tool_type_text("内容")
await mcp.tool_press_key("enter")
```

### 3. 清理 (可选)

```python
await mcp.tool_cleanup_isolated()
```

---

## 坐标映射

隔离模式使用与 computer-mcp 相同的百分比坐标 + 窗口区域转换:

```python
# 1. 获取浏览器窗口
rect = await mcp.tool_get_browser_rect()

# 2. AI 估算百分比坐标
pct_x, pct_y = 0.47, 0.25

# 3. 转换为实际坐标
real_x = rect["left"] + int(rect["width"] * pct_x)
real_y = rect["top"] + int(rect["height"] * pct_y)

# 4. 点击
await mcp.tool_click(real_x, real_y)
```

---

## 工具列表

| 工具 | 说明 |
|------|------|
| `tool_init_isolated` | 初始化隔离环境 |
| `tool_screenshot` | 截图 (自动切换桌面) |
| `tool_inspect_screen` | 截图 + OCR |
| `tool_click` | 点击 |
| `tool_double_click` | 双击 |
| `tool_drag` | 拖拽 |
| `tool_type_text` | 输入文字 |
| `tool_press_key` | 按键 |
| `tool_hotkey` | 组合键 |
| `tool_scroll` | 滚动 |
| `tool_wait` | 等待 |
| `tool_get_browser_rect` | 获取浏览器窗口位置 |
| `tool_confirm_action` | 请求确认 (在当前桌面) |
| `tool_cleanup_isolated` | 清理隔离环境 |

---

## 故障排除

### 虚拟桌面创建失败

**错误**: `无法初始化虚拟桌面 API`

**解决**:
1. 确认 Windows 版本 ≥ 10 1703 或 Win11
2. 安装 comtypes: `pip install comtypes`
3. 尝试以管理员权限运行

### 找不到浏览器窗口

**错误**: `未找到 Chrome 或 Edge 浏览器`

**解决**:
1. 安装 Chrome 或 Edge
2. 或修改 `isolated_browser.py` 中的 `BROWSER_PATHS`

### 桌面切换后窗口不可见

**排查**:
1. Win+Tab 查看所有虚拟桌面
2. 确认浏览器窗口在虚拟桌面 2
3. 检查窗口是否被最小化

---

## 与普通模式的对比

| 特性 | computer-mcp | isolated-computer-mcp |
|------|--------------|----------------------|
| 操作目标 | 当前前台窗口 | 隔离虚拟桌面中的窗口 |
| 用户干扰 | 会抢占焦点 | 完全无干扰 |
| 浏览器登录态 | 复用 | 复用 |
| 桌面切换 | 无 | 自动处理 |
| 适用场景 | 单一任务 | 并行工作 |

---

## 最佳实践

1. **初始化一次**: 一个会话中只调用一次 `tool_init_isolated`
2. **获取窗口位置**: 在截图后调用 `tool_get_browser_rect` 进行坐标映射
3. **及时清理**: 任务完成后调用 `tool_cleanup_isolated` 释放资源
4. **错误处理**: 捕获异常并记录日志
