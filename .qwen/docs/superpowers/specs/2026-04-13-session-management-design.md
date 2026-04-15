# 会话管理系统设计文档

**日期**: 2026-04-13  
**作者**: lyt  
**状态**: 待审核  

---

## 1. 需求概述

### 1.1 核心需求

用户需要一个轻量级的会话管理系统，用于在 AI 编程助手（Qwen Code / Claude Code）场景下：

1. **任务级会话管理** — 每次执行一个任务时开启一个 Main Session，在该任务下 fork 多个子 Session 并行处理
2. **Agent 任务分发** — Main Session 可以 fork 出多个子 Session，派发给不同的 Agent（通过新开终端窗口）执行
3. **跨 Agent 知识共享** — Agent A 在独立终端中工作，Agent B 可以通过读取任务面板发现 Agent A 的会话路径，从而获取其上下文
4. **灵活导出** — 支持导出整个会话文件或最近的几次对话片段

### 1.2 使用场景

```
用户开启终端窗口 = 启动一次任务（Main Session）
    ↓
在任务面板中注册多个子 Session，派发给不同 Agent
    ↓
每个 Agent 在独立终端窗口中工作
    ↓
Agent 通过读取任务面板发现其他 Agent 的会话信息
    ↓
需要时加载其他 Agent 的会话上下文
```

---

## 2. 架构设计

### 2.1 目录结构

```
.qwen/
└── sessions/                                    # 会话根目录
    │
    ├── task-isolated-mcp-20260413/             # 一次任务 = 一个目录
    │   ├── task-board.md                       # 任务面板（核心）
    │   ├── main-session.md                     # Main Session 对话记录
    │   │
    │   ├── isolated-mcp-testing/               # 子 Session A
    │   │   ├── 2026-04-13_15-30_tools.md       # 会话文件（自包含元数据）
    │   │   ├── 2026-04-13_15-45_test.md
    │   │   └── refs/                           # 挂载的引用（可选）
    │   │       └── from-agent-a_tools.md
    │   │
    │   └── weibo-development/                  # 子 Session B
    │       ├── 2026-04-13_16-00_api.md
    │       └── refs/
    │           └── from-isolated-mcp-testing_tools.md
    │
    ├── task-weibo-20260414/                    # 另一次任务
    │   ├── task-board.md
    │   └── ...
    │
    └── task-xiaohongshu-20260415/              # 又一次任务
        ├── task-board.md
        └── ...

scripts/
└── session-manager.py                          # 会话管理脚本
```

### 2.2 文件规范

#### 2.2.1 会话文件格式

每个 `.md` 文件开头包含 YAML Frontmatter：

```yaml
---
session_id: isolated-mcp-testing
session_name: "isolated-mcp 测试"
parent_task: task-isolated-mcp-20260413
parent_session: main-session
created: "2026-04-13T15:30:00"
updated: "2026-04-13T15:45:00"
status: active              # active | completed | archived
agent: agent-a              # 执行此会话的 Agent
tags: [isolated-mcp, 测试]
refs:                       # 挂载的其他会话
  - from_session: isolated-mcp-testing
    file: refs/from-agent-a_tools.md
    purpose: "工具参考"
---
```

#### 2.2.2 任务面板格式

```markdown
---
task_name: "isolated-mcp 测试与微博开发"
task_id: task-isolated-mcp-20260413
created: "2026-04-13T10:00:00"
updated: "2026-04-13T16:30:00"
---

# 任务面板：isolated-mcp 测试与微博开发

## Agent 列表

### Agent A
- **身份**: isolated-mcp 测试
- **会话**: `isolated-mcp-testing/`
- **状态**: working

### Agent B
- **身份**: 微博开发
- **会话**: `weibo-development/`
- **状态**: working
```

---

## 3. 核心工作流程

### 3.1 初始化任务

```bash
python scripts/session-manager.py init-task \
  --name "isolated-mcp 测试与微博开发"
```

**效果**：
1. 创建 `sessions/task-isolated-mcp-20260413/` 目录
2. 创建 `task-board.md`（空的任务面板）
3. 创建 `main-session.md`（Main Session 对话记录）

### 3.2 Fork 子 Session

```bash
python scripts/session-manager.py fork \
  --agent "Agent A" \
  --identity "isolated-mcp 测试" \
  --name isolated-mcp-testing
```

**效果**：
1. 创建子目录 `isolated-mcp-testing/`
2. 创建初始会话文件
3. 在 `task-board.md` 中注册 Agent A

### 3.3 导出会话

#### 导出整个会话

```bash
python scripts/session-manager.py export \
  --from isolated-mcp-testing \
  --to weibo-development \
  --mode full \
  --purpose "需要完整的测试上下文"
```

#### 导出最近 N 次对话

```bash
python scripts/session-manager.py export \
  --from isolated-mcp-testing \
  --to weibo-development \
  --mode recent \
  --count 3 \
  --purpose "需要最近的测试进展"
```

#### 导出特定文件

```bash
python scripts/session-manager.py export \
  --from isolated-mcp-testing \
  --file "2026-04-13_15-30_isolated-mcp-tools.md" \
  --to weibo-development \
  --purpose "工具列表参考"
```

### 3.4 查看任务面板

```bash
python scripts/session-manager.py board
```

**输出**：
```
📋 任务面板：isolated-mcp 测试与微博开发
═══════════════════════════════════════

🟢 Agent A
   身份: isolated-mcp 测试
   会话: isolated-mcp-testing/
   状态: working

🟢 Agent B
   身份: 微博开发
   会话: weibo-development/
   状态: working
```

### 3.5 查看会话树

```bash
python scripts/session-manager.py tree
```

**输出**：
```
📊 会话树：task-isolated-mcp-20260413
═══════════════════════════════════════

🟢 main-session
   创建: 2026-04-13 10:00

   ├── 🟢 isolated-mcp-testing
   │   创建: 2026-04-13 15:30
   │   导出 → weibo-development
   │
   └── 🟢 weibo-development
       创建: 2026-04-13 16:00
       引用 ← isolated-mcp-testing
```

---

## 4. 脚本命令参考

| 命令 | 用途 | 参数 |
|------|------|------|
| `init-task` | 初始化新任务 | `--name`, `--dir` |
| `fork` | 创建子 Session 并注册到任务面板 | `--agent`, `--identity`, `--name` |
| `export` | 导出会话/片段到其他会话 | `--from`, `--to`, `--file`, `--mode`, `--count`, `--purpose` |
| `board` | 查看当前任务面板 | 无 |
| `tree` | 查看会话树 | 无 |
| `list` | 列出所有会话 | 无 |
| `update-status` | 更新 Agent 状态 | `--agent`, `--status` |
| `unregister` | 从任务面板注销 Agent | `--agent` |

---

## 5. 错误处理

### 5.1 会话不存在

```
❌ 错误：会话 'xxx' 不存在
   提示：使用 'session-manager.py list' 查看所有会话
```

### 5.2 导出文件不存在

```
❌ 错误：文件 'xxx.md' 在会话 'yyy' 中不存在
   提示：使用 'session-manager.py list --session yyy' 查看文件列表
```

### 5.3 任务面板不存在

```
❌ 错误：当前目录下未找到任务面板
   提示：使用 'session-manager.py init-task' 初始化任务
```

---

## 6. 测试计划

### 6.1 单元测试

- 测试会话创建
- 测试任务面板更新
- 测试导出功能（full/recent/file）
- 测试引用关系追踪

### 6.2 集成测试

- 完整工作流：init-task → fork → export → board
- 多任务并行：创建两个任务，互不干扰
- 跨会话引用：Agent A 导出，Agent B 挂载

---

## 7. 后续扩展

### 7.1 可选增强

- [ ] 自动生成会话树可视化（Graphviz）
- [ ] 支持搜索所有任务中的关键词
- [ ] 任务完成后的自动归档
- [ ] 集成到 Qwen Code Skill

### 7.2 不在此版本实现

- 数据库存储（保持纯文件方案）
- Web UI（保持命令行 + Markdown）
- 实时同步（保持异步解耦）
