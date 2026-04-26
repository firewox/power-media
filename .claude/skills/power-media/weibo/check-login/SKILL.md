---
name: weibo-check-login
description: |
  使用 CDP (Chrome DevTools Protocol) + Ollama Vision 检查微博登录状态。

  当用户说以下任何内容时触发此 skill：
  - "检查微博登录状态"
  - "微博是否登录"
  - "查看微博登录"
  - "check weibo login"
  - "微博登录了吗"
  - 任何涉及检查微博登录状态的请求

  脚本执行：
  ```bash
  python weibo/check-login/scripts/check_login.py
  ```

  检测链路（三级降级）：
  1. CDP Network.getCookies → 精确检测 SUB Cookie
  2. Ollama Vision → 本地视觉模型分析截图
  3. 兜底 → 返回截图路径，由外部 AI 判断

  依赖：
  - websocket-client (pip install websocket-client) — CDP WebSocket 连接
  - Ollama 本地服务 (http://localhost:11434)，用于第 2 层兜底
  - Python 3.8+
  - Edge / Chrome 浏览器（脚本自动启动时带 CDP 参数，无需手动配置）

compatibility:
  - Python >= 3.8
  - Windows 10/11
  - Edge / Chrome 浏览器（需开启 CDP 调试端口）
  - Ollama >= 0.1.0（兜底检测）
---

# 检查微博登录状态

## 前置条件

### 1. 安装依赖

```bash
pip install websocket-client
```

Ollama 本地服务（兜底检测用，可选）：
```bash
ollama serve
```

### 2. 浏览器

无需手动配置。脚本在找不到微博窗口时**自动启动** Edge/Chrome 并附加以下参数：
- `--remote-debugging-port=9222` — 开启 CDP 调试端口
- `--remote-allow-origins=*` — 允许本地 WebSocket 连接

若浏览器已通过快捷方式手动配置了这些参数，脚本会优先复用现有实例。

## 脚本调用

### 直接执行脚本
```bash
python weibo/check-login/scripts/check_login.py
```

### 从其他脚本调用
```python
import subprocess
import json

result = subprocess.run(
    ["python", "weibo/check-login/scripts/check_login.py"],
    capture_output=True,
    text=True
)

# 解析 JSON 输出（最后一行）
output_lines = result.stdout.strip().split('\n')
json_line = output_lines[-1]
status = json.loads(json_line)

if status["loggedIn"] is True:
    print(f"已登录 (检测方式: {status.get('method')})")
elif status["loggedIn"] is False:
    print(f"未登录 (检测方式: {status.get('method')})")
else:
    # loggedIn 为 None 时，查看截图人工判断
    print(f"无法自动判断，请查看截图: {status.get('screenshot_path')}")
```

## 工作流程

脚本内部执行以下步骤：

### Step 1: 查找或打开微博窗口

优先查找现有浏览器窗口（标题含"微博"且进程为浏览器）。找不到时自动启动 Edge/Chrome 带 `--remote-debugging-port=9222 --remote-allow-origins=*`，复用已保存的登录状态（Cookie）。

启动时先不传微博 URL，而是通过 `webbrowser.open()` 在当前浏览器实例中打开 weibo.com，避免与浏览器崩溃恢复导致的重复标签页冲突。

### Step 2: 三级检测链路

#### 第 1 层：CDP Cookie 检测（最精确）

扫描 localhost 9222~9225 端口，找到 CDP 调试端口后：
1. `GET /json` → 找到 weibo.com 页面的 `webSocketDebuggerUrl`
2. WebSocket 连接 → 调用 `Network.getCookies` 协议方法
3. 检查是否存在 `SUB` Cookie（微博会话 Cookie，HttpOnly，无法从 JS 读取）

**优点**：不受 DOM 变化影响，无论 HttpOnly 都能读取，1 秒内完成。

#### 第 2 层：Ollama Vision 兜底（CDP 不可用时）

CDP 端口不可用时自动降级：
1. PIL 全屏截图
2. 调用 Ollama Vision（`qwen3.5:397b-cloud`）分析截图
3. 根据页面视觉特征判断：有「登录+注册」按钮 → 未登录；有用户昵称/头像 → 已登录

**触发场景**：浏览器未开启 CDP 端口、websocket-client 未安装。

#### 第 3 层：截图兜底（Ollama 也不可用时）

返回截图路径，`loggedIn: null`，由调用方（Claude 等多模态 AI）人工判断。

## 输出结果

**CDP 检测成功（已登录）：**
```json
{
  "loggedIn": true,
  "userName": null,
  "screenshot_path": "C:\\...\\weibo_shot_xxx.png",
  "method": "cdp",
  "cookie_domain": ".weibo.com"
}
```

**CDP 检测成功（未登录）：**
```json
{
  "loggedIn": false,
  "userName": null,
  "screenshot_path": "C:\\...\\weibo_shot_xxx.png",
  "method": "cdp",
  "cookie_count": 12
}
```

**Ollama Vision 兜底：**
```json
{
  "loggedIn": true,
  "userName": null,
  "screenshot_path": "C:\\...\\weibo_shot_xxx.png",
  "method": "ollama_vision",
  "reason": "页面顶部显示用户昵称，无登录按钮"
}
```

**无法自动判断（第 3 层兜底）：**
```json
{
  "loggedIn": null,
  "userName": null,
  "screenshot_path": "C:\\...\\weibo_shot_xxx.png",
  "method": "fallback",
  "cdp_error": "CDP 端口不可用",
  "ollama_error": "ollama_vision 模块不可用"
}
```

## 使用示例

**示例 1：CDP 正常**
```
用户：检查微博登录状态
AI：调用脚本...
结果：已登录 (检测方式: cdp)
```

**示例 2：无 CDP，Ollama 兜底**
```
用户：微博是否登录？
AI：调用脚本...
结果：未登录 (检测方式: ollama_vision)
```

**示例 3：全部降级**
```
用户：检查微博登录状态
AI：调用脚本...
结果：无法自动判断
      请查看截图: C:\...\weibo_shot_xxx.png
```

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 找不到微博窗口 | 自动打开默认浏览器并访问 weibo.com |
| CDP 端口不可用 | 降级到 Ollama Vision |
| websocket-client 未安装 | 降级到 Ollama Vision |
| 未找到 weibo.com 标签页 | 降级到 Ollama Vision |
| Ollama 服务不可用 | 降级到第 3 层，返回截图 |
| 页面加载超时 | 等待 5 秒后重试 |

## 注意事项

1. 脚本会自动启动浏览器并附加 CDP 参数，无需手动配置
2. 若浏览器已在运行但未开启 CDP 端口，CDP 检测会降级到 Ollama Vision
3. `SUB` Cookie 是微博的 HttpOnly 会话 Cookie，存在即表示已登录
4. 窗口标题应包含 "微博" 以便 focus_window 识别
5. `loggedIn: null` 表示所有检测方式均失败，需人工查看截图
