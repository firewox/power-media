# Agent 调用协议

**版本**: 3.0
**日期**: 2026-04-11
**适用范围**: power-media 项目所有 Skills

---

## 1. 架构说明

本项目采用**单 Agent 架构**：

- **当前 Agent**: 当前正在运行的 AI Agent（如 Claude、Kimi、Gemini 等）
- **职责**: 直接调用 computer-mcp 操作浏览器、编写代码、修改文件

**关键变更** (v3.0):
- 移除 multimodal-Qwen Sub-agent 架构
- 当前 Agent 直接调用 computer-mcp 工具
- 简化流程，减少中间层

---

## 2. 工具权限

当前 Agent 可直接使用所有工具：

| 工具类别 | 工具列表 | 用途 |
|---------|---------|------|
| **文件操作** | `read`, `write`, `edit` | 读写配置文件、编写代码 |
| **代码搜索** | `glob`, `grep` | 查找文件和内容 |
| **命令执行** | `bash` | 运行脚本和命令 |
| **MCP 工具** | `computer-mcp/*` | 截图、点击、输入、窗口控制 |
| **网络请求** | `webfetch` | 获取网页内容 |

**computer-mcp 工具列表**:
- `computer-mcp/screenshot`: 截取屏幕
- `computer-mcp/inspect_screen`: 截图 + OCR 分析（备选方案，主要使用多模态模型直接分析截图）
- `computer-mcp/click(x, y)`: 在坐标点击
- `computer-mcp/type_text(text)`: 输入文字
- `computer-mcp/press_key(key)`: 按单个键
- `computer-mcp/hotkey(keys)`: 按组合键
- `computer-mcp/focus_window(title)`: 聚焦窗口
- `computer-mcp/wait(seconds)`: 等待
- `computer-mcp/confirm_action(desc)`: 请求用户确认

---

## 3. 执行流程

### 3.1 使用 computer-mcp 的标准流程

```
用户请求 Skill (如：发微博)
    ↓
当前 Agent:
    ├── 1. 参数校验
    │      - 检查内容长度、格式等
    │
    ├── 2. 调用 computer-mcp 工具
    │      - focus_window("weibo")
    │      - screenshot()
    │      - click(x, y)
    │      - type_text("内容")
    │      - 截图验证结果
    │
    └── 3. 返回结果给用户
           - 成功/失败状态
           - 执行详情
```

### 3.2 示例：发布微博

```python
# Agent 直接执行流程

async def weibo_post_text(text: str):
    """发布微博"""

    # 1. 参数校验
    if len(text) > 140:
        return {"error": "内容超过140字符"}

    # 2. 调用 computer-mcp 执行操作
    try:
        # 聚焦窗口
        await mcp.tool_focus_window("weibo")
        await mcp.tool_wait(1)

        # 截图分析（多模态模型直接分析截图）
        screenshot = await mcp.tool_screenshot()
        # 【多模态 AI 分析】识别输入框位置 (x, y)

        # 点击输入框
        await mcp.tool_click(x, y)

        # 输入内容
        await mcp.tool_type_text(text)

        # 截图验证输入成功
        screenshot = await mcp.tool_screenshot()
        # 【多模态 AI 验证】确认文字已输入

        # 找到发送按钮并点击
        # 【多模态 AI 分析】识别按钮位置
        await mcp.tool_click(x2, y2)

        # 请求确认
        confirmed = await mcp.tool_confirm_action("确认发布微博？")
        if not confirmed:
            return {"cancelled": True}

        # 验证结果
        screenshot = await mcp.tool_screenshot()
        # 【多模态 AI 验证】检查成功提示

        return {"success": True, "message": "微博发布成功"}

    except Exception as e:
        return {"success": False, "error": str(e)}
```

---

## 4. computer-mcp 最佳实践

### 4.1 截图分析流程

```python
# 标准截图分析流程（多模态模型）

# 1. 截图
screenshot_path = await mcp.tool_screenshot()

# 2. 多模态 AI 分析截图
# 【多模态模型识别】截图中的界面元素
# - 识别输入框、按钮、文字等 UI 元素
# - 理解页面当前状态（编辑页、预览页、成功提示等）
# - 返回元素的屏幕坐标 (x, y)

# 3. 基于分析执行操作
await mcp.tool_click(x, y)  # 根据 AI 分析的位置点击

# 4. 截图验证（同样由多模态模型分析）
screenshot_path = await mcp.tool_screenshot()
# 【多模态 AI 验证】确认操作结果
```

### 4.2 错误处理

```python
try:
    # 执行操作
    await mcp.tool_click(x, y)

    # 验证结果
    screenshot = await mcp.tool_screenshot()
    # 【分析】确认操作成功

except Exception as e:
    # 截图记录错误状态
    screenshot = await mcp.tool_screenshot()
    # 【分析】记录当前页面状态

    return {
        "success": False,
        "error": str(e),
        "screenshot": screenshot,  # 保存错误截图便于排查
        "context": "当前页面状态描述"
    }
```

### 4.3 使用 inspect_screen 优化

当需要 OCR 识别特定文字时（备选方案），使用 `inspect_screen`：

```python
# 截图 + OCR 分析（一次性完成）
# 注意：主要识别方式是多模态模型，OCR 仅在需要精确文字识别时使用
result = await mcp.tool_inspect_screen()
text = result.get("text", "")
```

---

## 5. Skill 实现指南

### 5.1 编写 Skill 脚本

```python
# weibo/post-text/scripts/post_text.py

import asyncio
import sys
sys.path.insert(0, r"D:\08_tmp\02_media\power-media")

from weibo.lib.computer_mcp_client import ComputerMCPClient

async def post_weibo(text: str):
    """发布微博"""
    client = ComputerMCPClient()

    try:
        # 1. 打开浏览器（如未打开）
        import webbrowser
        webbrowser.open("https://weibo.com")
        await asyncio.sleep(3)

        # 2. 聚焦窗口
        await client.focus_window("微博")
        await client.wait(1)

        # 3. 截图分析
        screenshot = await client.screenshot()
        # 【Agent 分析截图】找到输入框位置

        # 4. 点击输入框
        await client.click(100, 200)  # 根据截图调整坐标

        # 5. 输入文字
        await client.type_text(text)

        # 6. 截图验证
        screenshot = await client.screenshot()

        # 7. 点击发送
        await client.click(500, 300)  # 根据截图调整坐标

        # 8. 确认操作
        confirmed = await client.confirm_action("确认发布微博？")
        if not confirmed:
            return {"cancelled": True}

        # 9. 验证结果
        screenshot = await client.screenshot()
        # 【Agent 分析截图】确认成功

        return {"success": True, "message": "发布成功"}

    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "测试微博"
    result = asyncio.run(post_weibo(text))
    print(result)
```

### 5.2 Skill 执行流程

```
用户: "发微博：今天天气真好"
    ↓
Agent:
    1. 读取 Skill 定义 (SKILL.md)
    2. 解析参数: text="今天天气真好"
    3. 调用对应脚本: python post_text.py "今天天气真好"
    4. 脚本内部调用 computer-mcp:
       - 打开浏览器
       - 截图分析
       - 点击输入
       - 截图验证
       - 点击发送
       - 确认操作
    5. 返回结果给用户
```

---

## 6. 性能优化

### 6.1 减少截图次数

**不好的做法**：
```python
await mcp.tool_click(x, y)
screenshot1 = await mcp.tool_screenshot()  # 立即截图
await mcp.tool_click(x2, y2)
screenshot2 = await mcp.tool_screenshot()  # 又截图
```

**好的做法**：
```python
await mcp.tool_click(x, y)
await mcp.tool_wait(0.5)  # 等待页面响应
await mcp.tool_click(x2, y2)
screenshot = await mcp.tool_screenshot()  # 只在需要验证时截图
```

### 6.2 使用 inspect_screen 代替 screenshot + 手动 OCR

```python
# 一次性获取截图和 OCR 结果
result = await mcp.tool_inspect_screen()
text = result.get("text", "")
```

---

## 7. 错误处理指南

### 7.1 常见错误场景

| 场景 | 处理方式 |
|------|---------|
| 窗口未找到 | 先打开浏览器，再重试 focus_window |
| 元素未找到 | 截图说明当前页面状态，返回错误 |
| 操作超时 | 增加 wait 时间，重试操作 |
| 用户取消确认 | 友好返回取消状态 |

### 7.2 重试策略

```python
max_retries = 3
for i in range(max_retries):
    try:
        await mcp.tool_click(x, y)
        # 验证成功则跳出
        break
    except Exception as e:
        if i == max_retries - 1:
            raise  # 最后一次重试失败
        await mcp.tool_wait(1)  # 等待后重试
```

---

## 8. 实施检查清单

### Skill 开发
- [ ] 确定需要哪些 computer-mcp 操作
- [ ] 编写参数校验逻辑
- [ ] 实现截图→分析→操作的循环
- [ ] 添加错误处理和重试机制
- [ ] 编写返回结果格式

### 测试验收
- [ ] 手动验证每个操作步骤
- [ ] 测试错误场景（窗口未打开、网络错误等）
- [ ] 测试取消操作
- [ ] 记录各元素的典型坐标位置

---

## 8. 隔离模式 (Isolated Mode)

### 8.1 何时使用隔离模式

当需要 AI 操作浏览器,而用户需要同时工作且互不干扰时,使用隔离模式。

### 8.2 配置

在 `.claude/settings.local.json` 中配置:

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

### 8.3 调用流程

```
用户请求 Skill
    ↓
1. 初始化隔离环境
   await mcp.tool_init_isolated(url)
    ↓
2. 获取浏览器窗口位置
   rect = await mcp.tool_get_browser_rect()
    ↓
3. 截图分析
   screenshot = await mcp.tool_screenshot()
   # AI 分析截图,估算百分比坐标
    ↓
4. 转换坐标并操作
   real_x = rect["left"] + int(rect["width"] * pct_x)
   real_y = rect["top"] + int(rect["height"] * pct_y)
   await mcp.tool_click(real_x, real_y)
    ↓
5. 重复 3-4 直到完成
    ↓
6. 清理 (可选)
   await mcp.tool_cleanup_isolated()
```

### 8.4 工具对照

| 普通模式 | 隔离模式 | 区别 |
|---------|---------|------|
| `tool_screenshot` | `tool_screenshot` | 隔离模式自动切换桌面 |
| `tool_click` | `tool_click` | 隔离模式自动切换桌面 |
| - | `tool_init_isolated` | 仅隔离模式 |
| - | `tool_get_browser_rect` | 仅隔离模式 |
| - | `tool_cleanup_isolated` | 仅隔离模式 |

### 8.5 注意事项

- 隔离模式需要 Windows 10 1703+ 或 Windows 11
- 初始化后才能使用其他工具
- 所有操作自动处理虚拟桌面切换
- `tool_confirm_action` 在当前桌面显示(不切换)

---

## 9. 快速参考

### 决策树

```
用户请求
    ↓
需要操作浏览器/桌面?
    ↓
    ├── 是 → 调用 computer-mcp 工具
    │         - screenshot/inspect_screen
    │         - click/type_text
    │         - 截图验证结果
    │
    └── 否 → 直接读写文件/执行命令
```

### 工具使用频率

| 工具 | 使用频率 | 说明 |
|------|---------|------|
| `screenshot` | ⭐⭐⭐⭐⭐ | 每次操作后验证，多模态模型分析 |
| `click` | ⭐⭐⭐⭐⭐ | 点击按钮、输入框 |
| `type_text` | ⭐⭐⭐⭐ | 输入文字内容 |
| `focus_window` | ⭐⭐⭐ | 确保窗口在前台 |
| `wait` | ⭐⭐⭐ | 页面加载等待 |
| `confirm_action` | ⭐⭐ | 高风险操作前确认 |
| `inspect_screen` | ⭐ | 备选方案，仅在需要精确 OCR 时使用 |

---

## 附录：版本历史

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|---------|
| 1.0 | 2026-04-11 | Claude | 初始版本 |
| 2.0 | 2026-04-11 | Claude | 引入 multimodal-Qwen Sub-agent 架构 |
| 3.0 | 2026-04-11 | Claude | **移除 Sub-agent，改为单 Agent 直接调用** |
| 3.1 | 2026-04-12 | Claude | **坐标映射规范**: 截图压缩导致坐标偏差，统一使用百分比坐标 + 窗口区域转换 |
| 3.2 | 2026-04-12 | Claude | **隔离模式**: 新增 isolated-mcp 模块,支持 Windows 虚拟桌面隔离 |

---

## 附录 A: 截图坐标映射规范 ⚠️ 重要

### 问题

多模态模型看到的截图会被**自动压缩**（如 2560x1600 → ~1280x800），导致：
- 模型基于压缩图估算的坐标 ≠ 实际屏幕坐标
- 直接点击偏差 50%~100%

### 解决方案

**所有 Skills 统一使用百分比坐标 + 窗口区域转换**：

```python
# 1. AI 估算百分比（基于看到的截图）
input_box_pct = (0.47, 0.25)  # 水平 47%, 垂直 25%

# 2. 脚本获取浏览器窗口内容区域
window_rect = get_browser_window_rect()  # (left, top, width, height)

# 3. 转换为屏幕绝对坐标
real_x = window_rect.left + int(window_rect.width * pct_x)
real_y = window_rect.top + int(window_rect.height * pct_y)

# 4. 点击
pyautogui.click(real_x, real_y)
```

### 优势

- ✅ 适配不同屏幕分辨率
- ✅ 适配不同浏览器窗口大小
- ✅ 不受截图压缩影响

### 配套规则

1. **中文输入**: 使用 `pyperclip.copy() + Ctrl+V`，`pyautogui.typewrite` 不支持中文
2. **页面滚动**: 操作前 `Ctrl+Home` 回到顶部确保元素可见
3. **不确定时**: 使用标注脚本画出坐标让用户确认

详见 [COORDINATE-MAPPING-RULE.md](./COORDINATE-MAPPING-RULE.md)

---

**重要提示**: 当前 Agent 可以直接调用 computer-mcp 工具，无需通过 Sub-agent。Agent 需要自行分析截图内容并决策操作。
