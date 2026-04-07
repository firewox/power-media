# Desktop-First Computer MCP Design

## 背景

`power-media` 需要在反爬、登录态复杂、DOM 不稳定的网页环境下完成平台操作。对于微博、小红书、微信公众号等场景，纯浏览器自动化不一定可靠，因此第一版采用桌面优先方案：AI 通过截图理解界面，再通过 MCP 工具控制鼠标、键盘和窗口，直接操控已打开的浏览器窗口。

## 目标

- 让 AI 能稳定操控 Windows 上的浏览器窗口。
- 将“看”和“动”统一收敛到一个本地 `computer-mcp` 服务。
- 支持截图识别、窗口聚焦、键鼠输入、滚动和高风险操作确认。
- 作为 `power-media` 各平台 skill 的统一执行层。

## 非目标

- 不做完整的浏览器 DOM 自动化主方案。
- 不依赖平台官方 API 作为主路径。
- 不在第一版覆盖所有桌面程序，只优先覆盖浏览器窗口。

## 总体架构

```text
Claude / Skills
   -> MCP client
      -> computer-mcp (local service)
         -> screenshot / OCR / window inspect
         -> mouse / keyboard / focus / scroll
         -> Windows automation backend
            -> UI Automation / Win32 / SendInput / image matching
```

核心原则：AI 不直接调用系统接口，只通过 MCP 工具请求动作。`computer-mcp` 负责把请求翻译成 Windows 能力，并在每次动作后提供新的视觉反馈。

## 架构分层

### 1) 感知层

负责采集当前屏幕和窗口状态。

- 全屏或指定窗口截图
- 当前鼠标位置
- 可见窗口列表
- 识别候选按钮、输入框、文本区域
- OCR 文本结果

### 2) 执行层

负责向系统发送操作。

- 点击、双击、拖拽
- 文本输入
- 热键和单键
- 滚轮和页面滚动
- 窗口聚焦、最小化、恢复

### 3) 协调层

负责把识别结果转成动作序列，并做验证。

- 根据截图判断下一步操作
- 执行动作后再次截图确认
- 失败时重试、换策略或请求人工确认

## 模块划分

### `computer-mcp`

本地 MCP 服务入口，负责暴露统一工具。

职责：
- 管理工具注册
- 处理来自 AI 的调用请求
- 调用 Windows backend
- 返回结构化结果和错误信息

### `windows-backend`

封装 Windows 相关能力。

建议组合：
- 截图：`mss` 或 Win32 GDI
- 输入：`SendInput` 或 `pyautogui`
- 窗口：`pywinauto` 或 UI Automation
- OCR：`PaddleOCR` 或 `EasyOCR`
- 图像匹配：`OpenCV`

### `screen-inspector`

把截图转换为可用的界面信号。

- OCR 文本块
- 输入框候选
- 按钮候选
- 可点击区域坐标

## 工具接口

最小可跑版本建议提供这些 MCP 工具：

- `screenshot`
- `list_windows`
- `focus_window`
- `click`
- `double_click`
- `drag`
- `type_text`
- `press_key`
- `hotkey`
- `scroll`
- `wait`
- `inspect_screen`
- `get_cursor`
- `confirm_action`

## 数据流

1. AI 先调用 `screenshot` 或 `inspect_screen`。
2. `computer-mcp` 返回截图路径、OCR 结果、候选控件和窗口信息。
3. AI 选择动作，例如点击某个按钮或输入文本。
4. `computer-mcp` 执行动作。
5. 系统再次截图验证状态变化。
6. 若未达到预期，进入重试、切换策略或人工确认。

## 错误处理

- 工具调用失败：返回明确错误码和原因。
- 元素未识别：允许重新截图、扩大搜索区域或降级为坐标点击。
- 窗口未聚焦：先执行 `focus_window` 再继续。
- 高风险动作：例如发布、删除、提交，必须走 `confirm_action`。
- 连续失败：记录上下文并停止自动执行，避免误操作。

## 安全边界

- 默认只控制已授权的本地会话。
- 高风险按钮点击前必须二次确认。
- 记录关键动作日志，便于回放和排查。
- 不保存敏感账号信息到日志。

## 与 power-media 的关系

- 平台 skill 只描述意图，不直接写死每个平台的鼠标坐标。
- `computer-mcp` 负责统一执行。
- 后续如果平台支持更稳定的方式，可以替换底层实现，但 skill 接口保持不变。

## 测试策略

- 单元测试：工具参数校验、错误码、动作编排。
- 集成测试：在本地浏览器窗口上验证截图、点击、输入、窗口切换。
- 回归测试：模拟发布页、草稿页、登录页和弹窗场景。
- 人工验收：确认关键动作是否安全、稳定、可恢复。

## 迭代顺序

1. 先实现截图、窗口列表、聚焦、点击、输入、热键。
2. 再接入 OCR 和 `inspect_screen`。
3. 再补滚动、拖拽、确认和重试。
4. 最后把 `weibo`、`rednote`、`wechat` 的 skill 接到该执行层。
