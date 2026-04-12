# 隔离模式设计文档 - Windows 虚拟桌面方案

**日期**: 2026-04-12
**状态**: 已批准
**版本**: 1.0

---

## 1. 概述

### 1.1 目标

为 power-media 项目实现"隔离模式",使得 AI Agent 在执行浏览器自动化操作时,与用户的日常工作完全并行隔离,互不干扰。

### 1.2 核心需求

| 需求 | 说明 |
|------|------|
| 完全并行隔离 | AI 操作不影响用户,用户操作不影响 AI |
| 复用浏览器登录态 | 不创建独立 Profile,共享 Cookie/Session |
| 用户完全无感知 | AI 操作在后台自动完成,用户看不到操作过程 |
| 单平台场景 | 每次只操作一个平台,用户在另一桌面正常工作 |
| 灵活操作模式 | AI 可有限访问系统资源(如文件选择器) |

### 1.3 技术方案

采用 **Windows 虚拟桌面 (Virtual Desktop)** 实现隔离:
- 用户在虚拟桌面 1 工作
- AI 在虚拟桌面 2 操作浏览器
- 同一浏览器进程,共享登录态
- AI 通过快速切换虚拟桌面完成截图和操作

---

## 2. 架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        power-media 项目                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  用户工作空间              隔离管理层              AI 工作空间    │
│  ┌──────────┐          ┌──────────────┐         ┌──────────┐  │
│  │虚拟桌面 1 │ ←隔离→  │ 虚拟桌面管理器│ ←控制→  │虚拟桌面 2 │  │
│  │          │          └──────┬───────┘         │          │  │
│  │ • 日常工作 │               │                 │ • 浏览器  │  │
│  │ • 任意操作 │               │                 │ • AI 操作 │  │
│  └──────────┘               │                 └──────────┘  │
│                             │                              │
│                    ┌────────▼────────┐                      │
│                    │  隔离浏览器管理  │                      │
│                    │  • 启动/定位窗口 │                      │
│                    │  • 移动桌面      │                      │
│                    └────────┬────────┘                      │
│                             │                              │
│                    ┌────────▼────────┐                      │
│                    │  隔离 MCP 服务   │                      │
│                    │  • 截图/点击     │                      │
│                    │  • 自动切换桌面   │                      │
│                    └─────────────────┘                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 组件关系

```
用户调用 Skill (如: 发微博)
    ↓
isolated-mcp/server.py
    ↓
    ├── VirtualDesktopManager    # 虚拟桌面管理
    │     └── 创建/切换/移动窗口
    │
    ├── IsolatedBrowser          # 隔离浏览器
    │     └── 启动/定位/获取窗口信息
    │
    └── IsolatedComputerMCP      # 隔离 MCP 工具
          └── 封装所有操作,自动切换桌面
```

---

## 3. 详细设计

### 3.1 虚拟桌面管理器 (VirtualDesktopManager)

**文件**: `isolated-mcp/virtual_desktop.py`

```python
class VirtualDesktopManager:
    """Windows 虚拟桌面管理器"""
    
    def create_desktop(self, name: str = "power-media-isolated") -> str:
        """
        创建新的虚拟桌面
        
        Args:
            name: 桌面名称(仅用于标识,Windows 不原生支持名称)
        
        Returns:
            desktop_id: 虚拟桌面的 GUID/标识符
        
        Raises:
            VirtualDesktopError: 创建失败时抛出
        """
    
    def switch_to_desktop(self, desktop_id: str) -> None:
        """
        切换到指定虚拟桌面
        
        Args:
            desktop_id: 目标桌面 ID
        
        Notes:
            - 切换是异步的,需要短暂等待
            - 切换后当前桌面的所有窗口会被隐藏
        """
    
    def get_current_desktop(self) -> str:
        """
        获取当前虚拟桌面的 ID
        
        Returns:
            desktop_id: 当前桌面 ID
        """
    
    def move_window_to_desktop(self, hwnd: int, desktop_id: str) -> None:
        """
        将指定窗口移动到目标虚拟桌面
        
        Args:
            hwnd: 窗口句柄
            desktop_id: 目标桌面 ID
        
        Notes:
            - 窗口会被移动到目标桌面,但不会自动激活
            - 如果目标桌面不存在,会抛出异常
        """
    
    def list_desktops(self) -> list[str]:
        """列出所有虚拟桌面 ID"""
    
    def cleanup(self, desktop_ids: list[str] = None) -> None:
        """
        清理指定的虚拟桌面
        
        Args:
            desktop_ids: 要清理的桌面 ID 列表,默认清理所有非默认桌面
        
        Notes:
            - 清理前会确保桌面上没有窗口
            - 不会清理用户创建的桌面(除非明确指定)
        """
```

**技术实现**:
- 使用 `comtypes` 库调用 Windows `IVirtualDesktopManager` COM 接口
- 需要 `CLSID_VirtualDesktop` 和 `IID_IVirtualDesktopManager`
- Windows 10 1703+ / Windows 11 支持

---

### 3.2 隔离浏览器 (IsolatedBrowser)

**文件**: `isolated-mcp/isolated_browser.py`

```python
class IsolatedBrowser:
    """隔离浏览器管理器"""
    
    def __init__(self, desktop_manager: VirtualDesktopManager):
        self.desktop_manager = desktop_manager
        self.desktop_id = None  # 隔离桌面的 ID
        self.window_hwnd = None  # 浏览器窗口句柄
    
    def setup(self, url: str = None) -> int:
        """
        初始化隔离浏览器环境
        
        流程:
        1. 创建/定位虚拟桌面
        2. 启动或定位浏览器窗口
        3. 将窗口移动到虚拟桌面
        4. 返回窗口句柄
        
        Args:
            url: 要打开的 URL(可选)
        
        Returns:
            hwnd: 浏览器窗口句柄
        """
    
    def launch_or_locate(self, url: str = None) -> int:
        """
        启动新浏览器窗口或定位已有窗口
        
        策略:
        1. 先查找已有的浏览器窗口(通过窗口类名/标题)
        2. 如果没有,启动新窗口 (复用默认 Profile)
        
        Args:
            url: 要打开的 URL(可选)
        
        Returns:
            hwnd: 窗口句柄
        """
    
    def move_to_isolated_desktop(self) -> None:
        """将浏览器窗口移动到隔离虚拟桌面"""
    
    def get_window_rect(self) -> dict:
        """
        获取浏览器窗口内容区域
        
        Returns:
            {
                "left": int,
                "top": int,
                "width": int,
                "height": int
            }
        
        Notes:
            - 使用 GetClientRect 获取内容区域(不含边框)
            - 用于坐标映射转换
        """
    
    def ensure_restored(self) -> None:
        """确保窗口处于恢复状态(非最小化/最大化)"""
    
    def ensure_minimized(self) -> None:
        """确保窗口最小化"""
    
    def is_alive(self) -> bool:
        """检查窗口是否仍然存活"""
    
    def cleanup(self) -> None:
        """清理隔离浏览器环境(可选关闭窗口)"""
```

**浏览器查找策略**:
```python
# 通过窗口类名查找常见浏览器
BROWSER_CLASS_NAMES = [
    "Chrome_WidgetWin_1",      # Chrome/Edge
    "MozillaWindowClass",     # Firefox
    "OperaWindowClass",       # Opera
]

# 通过窗口标题过滤
def is_browser_window(hwnd, title):
    # 排除 power-media 自己的窗口
    if "power-media" in title.lower():
        return False
    # 匹配浏览器特征
    return any(cls in get_class_name(hwnd) for cls in BROWSER_CLASS_NAMES)
```

---

### 3.3 隔离 MCP 服务 (IsolatedComputerMCP)

**文件**: `isolated-mcp/server.py`

```python
from mcp.server.fastmcp import FastMCP
from virtual_desktop import VirtualDesktopManager
from isolated_browser import IsolatedBrowser

mcp = FastMCP("isolated-computer-mcp")

# 全局隔离管理器
_isolated_manager = None

@mcp.tool()
def tool_init_isolated(browser_url: str = None) -> dict:
    """
    初始化隔离环境
    
    Args:
        browser_url: 浏览器要打开的 URL(可选)
    
    Returns:
        初始化结果,包含 desktop_id 和 window_hwnd
    """

@mcp.tool()
def tool_screenshot(region_top: int = 0, region_left: int = 0,
                    region_width: int = 0, region_height: int = 0) -> dict:
    """
    在隔离环境中截图
    
    流程:
    1. 切换到隔离虚拟桌面
    2. 恢复浏览器窗口
    3. 执行截图 (使用原有 take_screenshot 逻辑)
    4. 切回用户虚拟桌面
    5. 返回截图
    """

@mcp.tool()
def tool_click(x: int, y: int, button: str = "left") -> dict:
    """
    在隔离环境中点击
    
    流程:
    1. 切换到隔离虚拟桌面
    2. 聚焦浏览器窗口
    3. 执行点击
    4. 切回用户虚拟桌面
    """

# 其他工具类似...
# tool_double_click, tool_drag, tool_type_text, tool_press_key, etc.

@mcp.tool()
def tool_cleanup_isolated() -> dict:
    """清理隔离环境(关闭窗口、清理虚拟桌面)"""
```

### 3.4 桌面切换核心逻辑

```python
class IsolatedOperation:
    """隔离操作基类,自动处理桌面切换"""
    
    def __init__(self, desktop_manager, browser, operation):
        self.desktop_manager = desktop_manager
        self.browser = browser
        self.operation = operation  # 实际要执行的操作
    
    def execute(self, *args, **kwargs):
        user_desktop = self.desktop_manager.get_current_desktop()
        
        try:
            # 1. 切换到隔离桌面
            self.desktop_manager.switch_to_desktop(self.browser.desktop_id)
            time.sleep(0.1)  # 等待切换完成
            
            # 2. 确保窗口在前台
            self.browser.ensure_restored()
            focus_window_by_hwnd(self.browser.window_hwnd)
            time.sleep(0.1)
            
            # 3. 执行实际操作
            result = self.operation(*args, **kwargs)
            
            return result
        
        finally:
            # 4. 切回用户桌面 (确保无论成功失败都切回)
            self.desktop_manager.switch_to_desktop(user_desktop)
            time.sleep(0.05)
```

**优化要点**:
- 使用 `try/finally` 确保切回用户桌面
- 切换延迟控制在 100ms 内,用户几乎无感知
- 截图操作可以使用更短的延迟(50ms)

---

## 4. 项目结构

```
power-media/
├── computer-mcp/                    # 原有 MCP (保持不变)
│   ├── server.py
│   ├── windows_backend.py
│   ├── screen_inspector.py
│   └── ...
│
├── isolated-mcp/                    # 新增隔离 MCP 模块
│   ├── __init__.py
│   ├── server.py                    # 隔离模式 MCP 服务
│   ├── virtual_desktop.py           # 虚拟桌面管理
│   ├── isolated_browser.py          # 隔离浏览器管理
│   ├── isolated_operations.py       # 隔离操作封装
│   └── requirements.txt             # 依赖 (comtypes, pywin32 等)
│
├── docs/
│   ├── AGENT-CALLING-PROTOCOL.md    # 现有协议
│   └── isolated-mode.md             # 新增: 隔离模式使用说明
│
└── ...
```

---

## 5. 配置与使用

### 5.1 MCP 配置

用户在 `.claude/settings.local.json` 中配置隔离 MCP:

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

### 5.2 使用流程

```
1. 初始化隔离环境
   await mcp.tool_init_isolated("https://weibo.com")
   
2. 执行自动化操作 (所有工具自动处理桌面切换)
   screenshot = await mcp.tool_screenshot()
   await mcp.tool_click(x, y)
   await mcp.tool_type_text("内容")
   
3. 完成后清理 (可选)
   await mcp.tool_cleanup_isolated()
```

---

## 6. 安全与容错

### 6.1 异常处理

| 异常场景 | 处理策略 |
|---------|---------|
| 虚拟桌面创建失败 | 降级模式: 浏览器窗口最小化,操作时临时恢复 |
| 窗口被用户关闭 | 检测句柄失效,尝试重新定位或报错 |
| 桌面切换超时 | 记录日志,强制切回用户桌面 |
| 浏览器崩溃 | 检测进程状态,可选重启浏览器 |
| 登录态过期 | 截图识别登录页,通知用户 |

### 6.2 安全约束

- **不操作用户桌面**: 所有操作严格限制在隔离虚拟桌面
- **窗口精确匹配**: 通过句柄操作,不会误点其他窗口
- **登录态复用不泄露**: 不导出 Cookie,不修改浏览器数据
- **操作日志记录**: 所有操作记录到独立日志文件

---

## 7. 技术要求

### 7.1 系统要求

- Windows 10 1703+ 或 Windows 11
- Python 3.10+
- 需要管理员权限(虚拟桌面 API 可能需要)

### 7.2 依赖库

```txt
comtypes>=1.2.0       # COM 接口调用
pywin32>=306          # Windows API
pyautogui>=0.9.54     # 鼠标键盘操作 (复用)
mss>=9.0.0            # 截图 (复用)
```

### 7.3 Windows API 参考

```python
# 虚拟桌面相关接口
# IVirtualDesktopManager (Windows 10+)
# CLSID: {aa509086-5ca9-4c25-8f95-589d3c07b48a}
# IID:   {a5cd92ff-29be-454c-8d04-d82879fb3f1b}

# 主要方法:
# - CreateDesktopW()
# - SwitchDesktop()
# - MoveWindowToDesktop()
# - GetCurrentDesktop()
```

---

## 8. 与现有架构的兼容性

### 8.1 不影响现有功能

- 原有 `computer-mcp` 保持不变
- 用户可以选择使用普通模式或隔离模式
- 两种模式可以共存

### 8.2 Skill 适配

现有 Skill 需要选择使用哪个 MCP:

```python
# 普通模式 (现有)
from computer_mcp_client import ComputerMCPClient

# 隔离模式 (新增)
from isolated_mcp_client import IsolatedMCPClient
```

或者在 Skill 配置中指定:

```yaml
# SKILL.md
isolated_mode: true  # 启用隔离模式
```

---

## 9. 未来扩展

### 9.1 可能的增强

- **多隔离实例**: 同时运行多个隔离任务(需要多个虚拟桌面)
- **桌面快照**: 保存虚拟桌面状态,下次恢复
- **通知机制**: 任务完成时通知用户(如 Windows Toast)
- **超时保护**: AI 操作超时自动清理

### 9.2 暂不实现

- 后台截图 (不切桌面) - 技术限制,现代浏览器不支持
- 独立浏览器 Profile - 违背复用登录态的需求
- Linux/macOS 支持 - 虚拟桌面 API 是 Windows 特有的

---

## 10. 实施检查清单

### Phase 1: 核心功能
- [ ] 实现 VirtualDesktopManager
- [ ] 实现 IsolatedBrowser
- [ ] 实现隔离 MCP 服务
- [ ] 测试桌面切换
- [ ] 测试截图/点击在隔离环境中的工作

### Phase 2: 集成测试
- [ ] 与现有 computer-mcp 共存测试
- [ ] 浏览器登录态复用测试
- [ ] 用户操作不干扰测试
- [ ] 异常场景测试

### Phase 3: 文档与示例
- [ ] 编写 isolated-mode.md 使用文档
- [ ] 更新 AGENT-CALLING-PROTOCOL.md
- [ ] 提供示例 Skill

---

## 11. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| Windows API 变更 | 虚拟桌面功能失效 | 提供降级模式,测试多版本 Windows |
| 浏览器更新 | 窗口类名/行为变化 | 多种查找策略,定期验证 |
| 权限问题 | 无法创建虚拟桌面 | 记录权限要求,提供备选方案 |
| 性能开销 | 桌面切换延迟 | 优化切换逻辑,控制延迟在 100ms 内 |

---

**文档版本**: 1.0  
**最后更新**: 2026-04-12  
**作者**: AI Assistant  
**审核**: 待用户审核
