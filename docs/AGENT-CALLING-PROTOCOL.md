# Agent 调用协议

**版本**: 2.0  
**日期**: 2026-04-11  
**适用范围**: power-media 项目所有 Skills

---

## 1. 设计原则

本项目涉及三类核心任务，不同 AI 模型有不同的专长：

| 任务类型 | 要求 | 适用 Agent | 模型 |
|---------|------|-----------|------|
| **视觉分析** | 看懂截图、识别元素 | `multimodal-Qwen` | `alibaba-cn/qwen3.6-plus` |
| **Computer-MCP 操作** | 截图→分析→点击→验证的循环 | `multimodal-Qwen` | `alibaba-cn/qwen3.6-plus` |
| **纯编码实施** | 写代码、改文件、无视觉需求 | - (Main Agent) | `baidu-qianfan-coding-plan/kimi-k2.5` |

**Agent 配置**（在 `.opencode/agent.yml` 中）：
```yaml
agent:
  multimodal-Qwen:
    description: 多模态模型，可以读懂图片
    mode: subagent
    model: alibaba-cn/qwen3.6-plus
```

**核心原则**：
- **任何涉及 computer-mcp 的操作** → 必须由能看懂截图的模型执行（multimodal-Qwen）
- **纯代码任务** → 由 Kimi K2.5 执行

---

## 2. 模型分工矩阵

| 任务场景 | 使用 Agent | 模型 | 调用方式 | 说明 |
|---------|-----------|------|---------|------|
| **Skill 执行**<br>使用 computer-mcp 操作浏览器 | `multimodal-Qwen` | `alibaba-cn/qwen3.6-plus` | **Sub-agent** | 需要看懂屏幕截图，决策点击位置 |
| **截图分析**<br>识别界面元素、OCR 理解 | `multimodal-Qwen` | `alibaba-cn/qwen3.6-plus` | Sub-agent | 同上，作为 Skill 执行的一部分 |
| **代码编写**<br>写脚本、改代码、重构 | - (Main Agent) | `baidu-qianfan-coding-plan/kimi-k2.5` | 当前 Agent | 纯文本任务，不需要视觉 |
| **文件操作**<br>读/写/编辑配置文件 | - (Main Agent) | `baidu-qianfan-coding-plan/kimi-k2.5` | 当前 Agent | 纯文件操作 |
| **架构设计**<br>写文档、制定方案 | - (Main Agent) | `baidu-qianfan-coding-plan/kimi-k2.5` | 当前 Agent | 纯文本推理 |

---

## 3. 关键规则

### 3.1 何时启动 multimodal-Qwen Sub-agent

✅ **必须启动**（涉及 computer-mcp）：
- 使用 `tool_screenshot` 截图并分析
- 使用 `tool_click` 点击特定按钮（需要先识别位置）
- 使用 `tool_type_text` 在特定输入框输入（需要先定位）
- 使用 `tool_inspect_screen` OCR 识别
- 验证操作结果（如"检查是否显示成功提示"）
- 任何需要"看懂屏幕再操作"的流程

❌ **不需要启动**（纯代码/文本）：
- 编写 SKILL.md 文档
- 修改配置文件
- 重构代码结构
- 编写工具函数
- 不涉及 computer-mcp 的纯逻辑实现

### 3.2 Sub-agent 的边界

```
用户: "发微博：今天天气真好"

Main Agent (Kimi K2.5):
    判断: 需要使用 computer-mcp → 启动 Sub-agent
    
    启动 multimodal-Qwen Sub-agent:
        ├── 1. 调用 tool_focus_window("weibo")
        ├── 2. 调用 tool_screenshot()
        ├── 3. 【自己看懂截图】找到输入框位置
        ├── 4. 调用 tool_click(x, y)
        ├── 5. 调用 tool_type_text("今天天气真好")
        ├── 6. 调用 tool_screenshot() 验证输入成功
        ├── 7. 【自己看懂截图】找到发送按钮
        ├── 8. 调用 tool_click(x, y)
        ├── 9. 调用 tool_confirm_action("确认发布？")
        └── 10. 返回执行结果
    
    接收 Sub-agent 结果
    返回给用户: "微博发布成功！"
```

---

## 4. 调用协议详解

### 4.1 Vision-Operator Agent (multimodal-Qwen)

**角色定义**：
能看懂截图并操作 computer-mcp 的专用 Agent

**Agent 配置**：
```yaml
agent:
  multimodal-Qwen:
    description: 多模态模型，可以读懂图片
    mode: subagent
    model: alibaba-cn/qwen3.6-plus
```

**触发条件**：
- 用户请求涉及 computer-mcp 操作
- 需要基于视觉反馈做决策

**可用工具**：
- `computer-mcp/screenshot`
- `computer-mcp/inspect_screen`
- `computer-mcp/click`
- `computer-mcp/type_text`
- `computer-mcp/press_key`
- `computer-mcp/hotkey`
- `computer-mcp/focus_window`
- `computer-mcp/wait`
- `computer-mcp/confirm_action`

**调用方式**：
```python
task(
    description="描述任务",
    subagent_type="multimodal-Qwen",  # 使用配置的 agent 名称
    prompt="""
    你是一个能看懂屏幕截图并操作电脑的 AI 助手。
    
    你的任务: {task_description}
    
    可用工具:
    - computer-mcp/screenshot: 截取屏幕
    - computer-mcp/click(x, y): 在坐标 (x, y) 点击
    - computer-mcp/type_text(text): 输入文字
    - computer-mcp/press_key(key): 按单个键
    - computer-mcp/hotkey(keys): 按组合键
    - computer-mcp/focus_window(title): 聚焦窗口
    - computer-mcp/wait(seconds): 等待
    - computer-mcp/confirm_action(desc): 请求用户确认
    
    工作流程:
    1. 如需聚焦窗口，先调用 focus_window
    2. 截图了解当前状态
    3. 看清截图中的元素位置
    4. 执行点击或输入操作
    5. 截图验证操作结果
    6. 重复直到任务完成
    
    重要:
    - 每次操作后必须截图验证
    - 找不到元素时说明原因
    - 高风险操作前调用 confirm_action
    
    开始执行任务。
    """
)
```

### 4.2 Code Agent (Kimi K2.5 - Main Agent)

**角色定义**：
负责编写代码、文件操作、架构设计的 Agent

**模型**：`baidu-qianfan-coding-plan/kimi-k2.5`

**触发条件**：
- 纯代码编写任务
- 文件读写编辑
- 文档编写
- 协调 Sub-agent 执行

**可用工具**：
- `read` / `write` / `edit`
- `bash`
- `grep` / `glob`
- `task` (启动 multimodal-Qwen Sub-agent)

**重要**：Kimi K2.5 无法看懂截图，不能直接操作 computer-mcp。必须通过 `task()` 工具启动 multimodal-Qwen Sub-agent 来执行视觉相关任务。

---

## 5. 完整 Workflow 示例

### 场景 1: 发布微博（使用 computer-mcp）

```
用户: "发微博：今天天气真好"

Main Agent (Kimi K2.5) - 协调者:
    1. 参数校验
       - 检查 text 长度 ≤ 140 ✓
    
    2. 启动 Vision-Operator Sub-agent (multimodal-Qwen)
       
       Sub-agent 执行:
       ┌─────────────────────────────────────┐
       │ Step 1: 聚焦窗口                    │
       │   focus_window("weibo")             │
       │                                     │
       │ Step 2: 截图分析                    │
       │   screenshot() → 【看懂】找输入框   │
       │                                     │
       │ Step 3: 点击输入框                  │
       │   click(x, y)                       │
       │                                     │
       │ Step 4: 输入内容                    │
       │   type_text("今天天气真好")         │
       │                                     │
       │ Step 5: 截图验证                    │
       │   screenshot() → 【看懂】确认输入   │
       │                                     │
       │ Step 6: 找发送按钮                  │
       │   screenshot() → 【看懂】找按钮     │
       │   click(x, y)                       │
       │                                     │
       │ Step 7: 确认操作                    │
       │   confirm_action("确认发布？")      │
       │                                     │
       │ Step 8: 验证结果                    │
       │   screenshot() → 【看懂】找成功提示 │
       │                                     │
       │ 返回: {"success": true}             │
       └─────────────────────────────────────┘
    
    3. 返回用户: "微博发布成功！"
```

### 场景 2: 修改 Skill 文档（纯编码）

```
用户: "更新 weibo-post-text 的 SKILL.md"

Main Agent (Kimi K2.5) - 直接执行:
    1. 读取当前文档
       read("weibo/post-text/SKILL.md")
    
    2. 修改内容
       edit("...")
    
    3. 保存
       ✓ 完成
    
    4. 返回用户: "已更新文档"
    
    （不涉及 computer-mcp，不需要启动 Sub-agent）
```

---

## 6. Sub-agent 启动规范

### 6.1 启动参数

```yaml
Agent Type: Sub-agent
Model: Alibaba (China)\Qwen3.6 Plus
Role: Vision-Operator

System Prompt: |
  你是一个能看懂屏幕截图并操作电脑的 AI 助手。
  
  任务: {具体任务描述}
  
  可用工具:
  - computer-mcp/screenshot: 截取屏幕，返回图片路径
  - computer-mcp/click(x, y): 在坐标 (x, y) 点击
  - computer-mcp/type_text(text): 输入文字
  - computer-mcp/press_key(key): 按单个键
  - computer-mcp/hotkey(keys): 按组合键
  - computer-mcp/focus_window(title): 聚焦窗口
  - computer-mcp/wait(seconds): 等待
  - computer-mcp/confirm_action(desc): 请求确认
  
  重要规则:
  1. 每次操作后必须截图验证结果
  2. 看清截图中的元素后再点击
  3. 找不到元素时说明具体原因
  4. 发布/删除等高风险操作前必须 confirm_action
  
  请一步一步执行任务，每步说明你在截图中看到了什么。

Max Turns: 20  # 防止无限循环
Timeout: 120s  # 单次 Sub-agent 执行超时
```

### 6.2 输出格式

Sub-agent 应返回结构化结果：

```json
{
  "success": true/false,
  "message": "执行结果描述",
  "steps": [
    {"action": "screenshot", "observation": "看到微博首页，已登录"},
    {"action": "click(100, 200)", "observation": "输入框已激活"},
    {"action": "type_text('xxx')", "observation": "文字已输入"},
    {"action": "click(500, 300)", "observation": "发送按钮已点击"}
  ],
  "error": "如有错误，描述原因"
}
```

---

## 7. 错误处理

### 7.1 Sub-agent 执行失败

```python
# Main Agent (Kimi K2.5) 处理逻辑

try:
    result = await dispatch_subagent(
        model="Alibaba (China)\\Qwen3.6 Plus",
        task="发布微博",
        max_turns=20
    )
except SubAgentTimeout:
    # 策略1: 重试
    # 策略2: 分步骤执行（缩小任务范围）
    # 策略3: 提示用户手动完成
    await handle_timeout()
except SubAgentError as e:
    # 根据错误类型处理
    if "元素未找到" in e.message:
        await retry_with_alternative_strategy()
    else:
        raise
```

### 7.2 常见错误场景

| 场景 | Sub-agent 行为 | Main Agent 处理 |
|------|---------------|----------------|
| 找不到元素 | 截图说明"未找到XXX" | 重试或报错 |
| 操作超时 | 返回超时错误 | 检查网络/页面状态 |
| 用户取消确认 | 返回取消状态 | 友好提示用户 |
| 页面跳转异常 | 说明当前页面状态 | 重新导航或报错 |

---

## 8. 性能优化

### 8.1 减少 Sub-agent 调用

**不好的做法**（频繁启动）：
```
for step in task_steps:
    result = dispatch_subagent(step)  # ❌ 每步都启动
```

**好的做法**（批量执行）：
```
# 一次性让 Sub-agent 完成整个任务
result = dispatch_subagent(
    task="完成整个微博发布流程"
)
```

### 8.2 截图优化

- 使用 `inspect_screen` 代替 `screenshot`（自带 OCR）
- 不要连续截图（操作后等待 1-2 秒再截图）
- 复用上一次截图结果（如果页面未变化）

---

## 9. 实施检查清单

在实现 Skill 时，使用以下清单：

### Skill 开发
- [ ] 确定是否需要 computer-mcp
- [ ] 如需，定义 Sub-agent 的 task 描述
- [ ] 编写 System Prompt
- [ ] 定义返回格式
- [ ] 编写错误处理逻辑

### Main Agent 协调
- [ ] 参数校验（在 Main Agent 层做）
- [ ] 启动 Sub-agent 执行操作
- [ ] 解析 Sub-agent 返回结果
- [ ] 格式化输出给用户

### Sub-agent 执行
- [ ] 能看懂截图中的元素
- [ ] 操作后截图验证
- [ ] 错误时说明具体原因
- [ ] 高风险操作前确认

---

## 10. 示例代码

### 10.1 Main Agent 启动 Sub-agent

```python
# Main Agent (Kimi K2.5)

async def weibo_post_text(text: str):
    """发布微博 - Main Agent 协调"""
    
    # 1. 参数校验（Main Agent 做）
    if len(text) > 140:
        return {"error": "内容超过140字符"}
    
    # 2. 启动 Vision-Operator Sub-agent
    result = await task(
        description="发布微博",
        subagent_type="general",
        prompt=f"""
你是一个能操作电脑的 Vision-Operator Agent。

任务: 帮用户发布一条微博，内容是："{text}"

请使用 computer-mcp 工具完成：
1. 聚焦微博窗口（focus_window("weibo")）
2. 截图找到输入框位置
3. 点击输入框
4. 输入文字: {text}
5. 找到发送按钮并点击
6. 请求用户确认（confirm_action）
7. 验证发布成功

工具列表:
- computer-mcp/focus_window
- computer-mcp/screenshot  
- computer-mcp/click
- computer-mcp/type_text
- computer-mcp/confirm_action

每步截图验证，返回 JSON 格式结果。
"""
    )
    
    # 3. 解析结果并返回给用户
    return parse_result(result)
```

### 10.2 Sub-agent 执行流程

```python
# Sub-agent (Qwen3.6 Plus) 内部执行

async def execute_task(task_description):
    """Vision-Operator 执行任务"""
    
    # Step 1: 聚焦窗口
    await mcp.tool_focus_window("weibo")
    await mcp.tool_wait(1)
    
    # Step 2: 截图并分析
    screenshot = await mcp.tool_screenshot()
    # 【自己能看懂截图】找输入框位置
    # 假设在截图中看到输入框在 (100, 200)
    
    # Step 3: 点击输入框
    await mcp.tool_click(100, 200)
    
    # Step 4: 输入文字
    await mcp.tool_type_text("今天天气真好")
    
    # Step 5: 截图验证
    screenshot = await mcp.tool_screenshot()
    # 【自己能看懂】确认文字已输入
    
    # Step 6: 找发送按钮
    # 【自己能看懂】找到发送按钮在 (500, 300)
    await mcp.tool_click(500, 300)
    
    # Step 7: 确认
    await mcp.tool_confirm_action("确认发布微博？")
    
    # Step 8: 验证结果
    screenshot = await mcp.tool_screenshot()
    # 【自己能看懂】检查是否有"发布成功"
    
    return {"success": True, "message": "发布成功"}
```

---

## 附录 A: 快速参考卡

### 决策树

```
用户请求
    ↓
需要使用 computer-mcp?
    ↓
    ├── 是 → 启动 Qwen3.6 Plus Sub-agent
    │         └── 让 Sub-agent 完成整个操作流程
    │         └── Main Agent 只负责解析结果
    │
    └── 否 → Kimi K2.5 直接执行
              └── 写代码、改文件、编文档
```

### 工具权限矩阵

| 工具 | Qwen3.6 Plus<br/>(Sub-agent) | Kimi K2.5<br/>(Main Agent) |
|------|---------------------------|---------------------------|
| computer-mcp/* | ✅ 可用 | ❌ 不可用 |
| read/write/edit | ❌ 不直接 | ✅ 可用 |
| bash | ⚠️ 受限 | ✅ 可用 |
| task (启动 Sub-agent) | ❌ | ✅ 可用 |

---

**文档版本历史**

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|---------|
| 1.0 | 2026-04-11 | Claude | 初始版本 |
| 2.0 | 2026-04-11 | Claude | 重大调整：computer-mcp 操作由 Qwen3.6 Plus Sub-agent 执行 |
