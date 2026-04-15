# Session 归档：isolated-mcp 实现与 rednote 修复

**归档日期**: 2026-04-12  
**会话编号**: PM-20260412-001  
**提交哈希**: `d32d610`  
**分支**: `master`

---

## 📌 会话概述

本次会话主要完成了三项核心工作：
1. **isolated-mcp 隔离模式模块** - 基于 Windows 虚拟桌面的 AI 操作隔离系统
2. **rednote 搜索功能修复** - 解决搜索平台错误和坐标点击问题
3. **平台截图命名规范化** - 统一各平台截图文件前缀

---

## 🎯 完成的任务

### Task 1: isolated-mcp 隔离模式模块 ✅

**目标**: 实现 AI 在独立虚拟桌面中操作浏览器，与用户工作完全并行隔离。

**实现文件**:
```
isolated-mcp/
├── __init__.py                    # 模块初始化
├── virtual_desktop.py             # 虚拟桌面管理器 (235 行)
├── isolated_browser.py            # 浏览器窗口管理 (290 行)
├── isolated_operations.py         # 自动桌面切换 (106 行)
├── server.py                      # MCP 服务 (361 行)
├── requirements.txt               # 依赖声明
└── tests/
    ├── test_virtual_desktop.py    # 7 个测试
    ├── test_isolated_browser.py   # 10 个测试
    ├── test_isolated_operations.py # 5 个测试
    ├── test_server_import.py      # 5 个测试
    └── test_e2e.py                # 端到端测试
```

**测试**: 27 个单元测试全部通过

**技术决策**:
- 使用键盘快捷键 (Win+Ctrl+D/F4/方向键) 而非 COM API
- 原因：COM 接口在不同 Windows 版本中 IID 不兼容
- 自动处理 `用户桌面→隔离桌面→操作→切回用户桌面` 流程

---

### Task 2: rednote 搜索功能修复 ✅

**问题发现**: 搜索"郑州旅游"时，结果显示在浏览器地址栏搜索，而不是小红书页面内搜索。

**根因分析**:

| 问题 | 原因 | 影响 |
|------|------|------|
| 搜索在错误平台 | SKILL 文档未区分 creator vs explore | 搜索无结果 |
| 坐标点击失败 | 硬编码 (0.5, 0.08) 点中浏览器标签页 | 误触 Bilibili 标签 |
| URL 导航无效 | Ctrl+L 未正确聚焦地址栏 | 页面未跳转 |

**修复方案**:

```python
# 旧方案：坐标点击搜索框 ❌
search_pct_x = 0.5
search_pct_y = 0.08  # 太靠上，点中浏览器标签页
click(x, y)

# 新方案：URL 直接导航 ✅
search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"
navigate_to(search_url)
```

**测试结果**: "郑州旅游"搜索成功，返回正确结果页面

---

### Task 3: 平台截图命名规范 ✅

**问题**: `rednote/lib/computer_mcp_client.py` 的截图前缀为 `weibo_shot_`

**修复**:
```python
# 添加 PLATFORM 类属性
class ComputerMCPClient:
    PLATFORM = "weibo"    # weibo_shot_xxx.png
    PLATFORM = "rednote"  # rednote_shot_xxx.png
    PLATFORM = "zhihu"    # zhihu_shot_xxx.png
    PLATFORM = "wechat"   # wechat_shot_xxx.png

# 动态生成文件名
prefix = getattr(self, "PLATFORM", "unknown")
filename = f"{prefix}_shot_{timestamp}.png"
```

**影响文件**:
- `weibo/lib/computer_mcp_client.py`
- `rednote/lib/computer_mcp_client.py`

---

### Task 4: 文档更新 ✅

| 文件 | 变更 |
|------|------|
| `rednote/search/SKILL.md` | 添加平台区分规则、禁止硬编码坐标、URL 导航优先 |
| `docs/AGENT-CALLING-PROTOCOL.md` | 新增第 8 章隔离模式调用流程 |
| `rednote/docs/coordinate-reference.md` | 新建坐标参考文档 |
| `docs/COORDINATE-MAPPING-RULE.md` | 坐标映射规范 |

---

## 🐛 遇到的问题与解决

### 问题 1: 虚拟桌面 COM API 不兼容

**现象**: `comtypes` 无法初始化 `IVirtualDesktopManagerInternal`

**原因**: Windows 虚拟桌面 API 的 IID 在不同版本中变化

**解决**: 改用键盘快捷键方案
```python
# Win+Ctrl+D 创建新桌面
keybd_event(VK_LWIN, 0, 0, 0)
keybd_event(VK_CONTROL, 0, 0, 0)
keybd_event(ord('D'), 0, 0, 0)
# ... 释放按键
```

---

### 问题 2: 坐标点击误触浏览器标签页

**现象**: 点击搜索框时，点到了 Bilibili 标签页

**原因**: 百分比坐标 `(0.5, 0.08)` 基于窗口，但 Y=8% 在浏览器 chrome 区域

**解决**: 
1. 使用 URL 导航替代坐标点击
2. 记录坐标参考文档，明确浏览器 chrome 占 8-10% 高度

---

### 问题 3: navigate_to 导航失败

**现象**: 调用 `navigate_to()` 后 URL 未变化

**原因**: 
- `focus_window` 通过 substring 匹配找到错误窗口
- Ctrl+L 没有正确聚焦地址栏

**解决**:
- 发布功能改用 `open_browser()` 直接打开新窗口
- 增加页面验证步骤

---

## 📊 变更统计

```
58 files changed, 1001 insertions(+), 513 deletions(-)
```

**新增文件**: 17 个
- isolated-mcp 模块 (12 个文件)
- 文档 (5 个文件)

**修改文件**: 8 个
- rednote 核心逻辑 (3 个文件)
- 平台客户端 (2 个文件)
- 文档 (3 个文件)

---

## 💡 经验教训

### 1. 禁止硬编码坐标点击浏览器 UI

**规则**: 
- ❌ 不要通过固定坐标点击浏览器标签页、地址栏、搜索框
- ✅ 优先使用 URL 直接导航
- ✅ 坐标点击需要 AI 分析截图后给出精确位置

### 2. 平台用途必须明确区分

| 平台 | URL | 用途 |
|------|-----|------|
| 创作者平台 | `creator.xiaohongshu.com` | 发布笔记、数据管理 |
| 用户浏览页 | `www.xiaohongshu.com/explore` | 搜索、查看、点赞 |

### 3. 窗口焦点匹配要精确

- substring 匹配可能找到错误窗口
- 优先使用 `open_browser()` 打开新窗口
- 或在 SKILL 中明确指定窗口标题

---

## 📋 后续工作

### 高优先级
- [ ] 完善发布笔记功能：解决窗口焦点问题
- [ ] 测试 isolated-mcp 实际使用场景

### 中优先级
- [ ] 扩展 isolated-mcp 到微博、知乎、微信公众号
- [ ] 优化坐标映射机制

### 低优先级
- [ ] 任务完成通知机制
- [ ] 支持多隔离实例

---

## 🔗 相关文档

- [隔离模式使用指南](../isolated-mode.md)
- [Agent 调用协议](../AGENT-CALLING-PROTOCOL.md)
- [小红书坐标参考](../../rednote/docs/coordinate-reference.md)
- [坐标映射规范](../COORDINATE-MAPPING-RULE.md)

---

**归档完成** | 2026-04-12 | PM-20260412-001
