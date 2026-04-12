# RedNote Skills 迁移至 computer-mcp 技术规格书

**日期**: 2026-04-12
**状态**: 草稿 / 待评审
**参考文档**: [weibo 迁移规格书](../weibo/session-weibo.md), [微博迁移规格](./specs/2026-04-11-weibo-computer-mcp-migration.md)

---

## 1. 背景与目标

### 1.1 背景
当前 RedNote skills 使用 **Playwright** 进行浏览器自动化，存在以下问题：
- 依赖特定 DOM 选择器，页面改版后易失效
- 需要维护独立的浏览器实例和 Cookie 文件
- 与 `computer-mcp` 能力重复，架构不统一
- 不符合 `power-media` Desktop-First 架构设计

### 1.2 目标
将 RedNote skills 从 **Playwright Browser 模式** 迁移到 **computer-mcp Desktop 模式**：
- 通过截图，多模态 AI 直接视觉理解界面内容
- 使用 `computer-mcp` 工具控制鼠标、键盘操作浏览器
- 统一使用桌面已打开的浏览器窗口（Edge/Chrome）
- 复用系统浏览器的登录态，无需独立管理 Cookie
- 降低维护成本，提升稳定性和真实用户行为模拟

### 1.3 非目标
- 不修改 `computer-mcp` 本身的实现
- 不改变 skill 的对外触发条件（保持向后兼容）
- 不直接操作小红书 API（仍使用创作者平台网页版）

---

## 2. 架构变化

### 2.1 当前架构（Playwright）
```
User Request
    ↓
RedNote Skill (Node.js)
    ↓
Playwright → Launch Chromium → DOM Operation → Return Result
    ↓
独立浏览器实例（需管理 Cookie、登录态）
```

### 2.2 目标架构（computer-mcp）
```
User Request
    ↓
RedNote Skill (Python / Skill Logic)
    ↓
computer-mcp (MCP Server)
    ├── inspect_screen           (截图，多模态 AI 直接视觉理解)
    ├── focus_window             (窗口管理)
    ├── click / type_text / hotkey (执行操作)
    └── confirm_action           (安全确认)
    ↓
Desktop Browser (用户已打开的 Edge/Chrome)
    └─ 复用已保存的登录态 Cookie
```

### 2.3 核心技术方案

**方案 A: 系统浏览器复用（推荐）**
- 通过 `win32gui` 查找已打开的小红书创作者平台窗口
- 复用系统浏览器的登录态，无需重新登录
- 在新标签页或当前页面操作
- 行为更像真实用户，降低风控风险

**方案 B: 独立浏览器启动（备用）**
- 如系统浏览器未打开，使用 computer-mcp 启动浏览器
- 访问 creator.xiaohongshu.com
- 需要用户手动扫码登录

---

## 3. 技术实现要点

### 3.1 坐标系统：百分比坐标映射

**问题根源**：
```
实际屏幕分辨率: 2560x1600 像素
AI 看到的截图: 约 1280x800（上传时被压缩）
AI 估算坐标: (600, 200) ← 基于压缩后的截图
实际点击: (600, 200) ← 但 pyautogui 操作的是 2560x1600 的屏幕
结果: 偏差巨大！
```

**解决方案**：
```python
# 1. AI 分析截图后，估算百分比坐标 (0~1)，不依赖截图尺寸
#    例: 输入框 (0.47, 0.25)，发布按钮 (0.61, 0.28)

# 2. 脚本获取浏览器窗口内容区域（扣除标题栏、边框）
window_rect = get_browser_window_rect()
# 返回: {"left": 0, "top": 0, "width": 2560, "height": 1528}

# 3. 转换为屏幕绝对坐标
real_x = window_rect.left + int(window_rect.width * pct_x)
real_y = window_rect.top + int(window_rect.height * pct_y)

# 4. pyautogui 精确点击
pyautogui.click(real_x, real_y)
```

### 3.2 浏览器窗口管理

```python
class RedNoteAutomation:
    def find_or_open_creator(self) -> bool:
        """查找或打开小红书创作者平台窗口"""
        # 尝试查找已打开的窗口
        titles = ["小红书创作者中心", "creator.xiaohongshu", "小红书"]
        for title in titles:
            if self.mcp.focus_window(title):
                return True
        
        # 未找到，打开浏览器
        self.mcp.open_browser("https://creator.xiaohongshu.com/")
        self.mcp.wait(5)
        return True
    
    def check_login_status(self) -> Dict:
        """检查登录状态，返回截图供 AI 分析"""
        result = self.mcp.inspect_screen()
        return {
            "loggedIn": None,  # 由 AI 分析截图判断
            "screenshot_path": result.get("screenshot_path"),
        }
```

### 3.3 中文输入支持

```python
def type_text(self, text: str) -> Dict:
    """输入文本（支持中文，通过剪贴板粘贴）"""
    import pyperclip
    import pyautogui
    pyperclip.copy(text)
    pyautogui.hotkey('ctrl', 'v')
    return {"success": True, "length": len(text)}
```

### 3.4 核心依赖库

复用 weibo 已有的 `computer_mcp_client.py`，新增 RedNote 专用封装：

```
rednote/
├── lib/
│   ├── computer_mcp_client.py      # 复用 weibo 的客户端（或提升到项目级）
│   └── rednote_automation.py       # 小红书专用自动化封装
└── ... (skills)
```

---

## 4. Skill 迁移详单

### 4.1 基础设施 Skills

#### check-login → rednote-check-login
**功能**: 检查小红书创作者平台登录状态

**迁移方案**:
| 步骤 | 动作 | computer-mcp 工具 |
|------|------|------------------|
| 1 | 聚焦/打开创作者平台窗口 | `find_or_open_creator()` |
| 2 | 截取当前页面 | `inspect_screen()` |
| 3 | AI 分析截图判断登录状态 | 检查是否有用户头像/登录二维码 |
| 4 | 返回结果 | `{"loggedIn": true/false, "screenshot_path": "..."}` |

**识别逻辑**:
- 检测到登录二维码 → 未登录
- 检测到用户头像/昵称（右上角）→ 已登录
- URL 包含 `/new/home` 且显示创作者中心内容 → 已登录

**SKILL.md 示例**:
```yaml
---
name: rednote-check-login
description: |
  检查小红书创作者平台登录状态。

  触发条件：
  - "检查小红书登录状态"
  - "小红书登录了吗"
  - "查看小红书是否登录"

  工作流程：
  1. 调用 computer-mcp/focus_window 聚焦创作者平台窗口
  2. 调用 computer-mcp/inspect_screen 截图识别
  3. AI 分析截图判断登录状态

  依赖：
  - computer-mcp
  - 浏览器已打开 creator.xiaohongshu.com 页面

compatibility:
  - computer-mcp >= 1.0
  - Windows 10/11
  - Edge / Chrome 浏览器
---

# 检查小红书登录状态

## 工作流程

### Step 1: 聚焦窗口
```json
{"tool": "computer-mcp/focus_window", "params": {"title": "小红书创作者中心"}}
```

### Step 2: 截图识别
```json
{"tool": "computer-mcp/inspect_screen", "params": {}}
```

### Step 3: AI 分析
- 检测到二维码 → 未登录
- 检测到用户头像 → 已登录

## 输出结果
```json
{
  "success": true,
  "loggedIn": true,
  "screenshot_path": "D:\\...\\rednote_shot_xxx.png"
}
```
```

---

#### get-qrcode → rednote-get-qrcode
**功能**: 获取登录二维码（如未登录）

**迁移方案**:
| 步骤 | 动作 | computer-mcp 工具 |
|------|------|------------------|
| 1 | 聚焦/打开创作者平台 | `find_or_open_creator()` |
| 2 | 检查是否已登录 | `inspect_screen()` |
| 3 | 如未登录，截图显示二维码 | `inspect_screen()` |
| 4 | 返回截图 | 供用户扫码 |
| 5 | 循环检测登录状态 | 每 3 秒截图一次，最多 2 分钟 |

**注意**: 二维码有效期约 2 分钟，超时需刷新页面

---

### 4.2 内容发布 Skills

#### publish-note → rednote-publish-note
**功能**: 发布图文笔记

**迁移方案**:
| 步骤 | 动作 | computer-mcp 工具 |
|------|------|------------------|
| 1 | 前置检查 | 调用 `rednote-check-login` 确认已登录 |
| 2 | 聚焦创作者平台 | `focus_window("小红书创作者中心")` |
| 3 | 导航到发布页 | `hotkey("ctrl l")` → `type_text("creator.xiaohongshu.com/publish/publish")` → `press_key("enter")` |
| 4 | 等待页面加载 | `wait(3)` + `inspect_screen()` 确认 |
| 5 | 点击"上传图文" | `inspect_screen()` 找"上传图文"按钮 → `click(x, y)` |
| 6 | 上传图片 | `inspect_screen()` 找上传区域 → `click(x, y)` → 文件选择对话框 |
| 7 | 输入图片路径 | `type_text("图片路径")` → `press_key("enter")` |
| 8 | 等待上传完成 | `wait(5)` + 循环检查 |
| 9 | 填写标题 | `inspect_screen()` 找标题输入框 → `click` → `type_text("标题")` |
| 10 | 填写正文 | `inspect_screen()` 找正文编辑器 → `click` → `type_text("内容")` |
| 11 | 添加话题标签 | `type_text("#话题")` → `press_key("enter")` |
| 12 | 点击发布 | `inspect_screen()` 找"发布"按钮 → `click(x, y)` |
| 13 | 确认发布 | `confirm_action("确认发布小红书笔记？")` |
| 14 | 验证结果 | `inspect_screen()` 检查"发布成功"提示 |

**内容校验**:
- 标题长度 ≤ 20 字
- 正文长度 ≤ 1000 字
- 图片数量 ≤ 18 张
- 话题标签 ≤ 10 个

**SKILL.md 关键步骤**:
```yaml
## 工作流程（简化版）

1. 检查登录状态
2. 导航到发布页
3. 选择"上传图文"
4. 上传图片文件
5. 填写标题和正文
6. 添加话题标签
7. 确认发布
8. 验证结果

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 笔记标题（≤20字） |
| content | string | 是 | 笔记正文（≤1000字） |
| images | string[] | 是 | 图片路径数组（≤18张） |
| tags | string[] | 否 | 话题标签数组（≤10个） |

## 输出结果
```json
{
  "success": true,
  "message": "笔记发布成功",
  "screenshot_path": "..."
}
```
```

---

#### publish-video → rednote-publish-video
**功能**: 发布视频笔记

**迁移方案**: 与 publish-note 类似，区别在于：
| 步骤 | 差异 | 说明 |
|------|------|------|
| 5 | 点击"上传视频" | 而非"上传图文" |
| 6 | 上传视频文件 | 支持 MP4 格式 |
| 9 | 填写封面标题 | 视频封面图上的标题 |
| 11 | 设置视频分类 | 可选 |

**视频要求**:
- 格式：MP4
- 大小：建议 ≤ 2GB
- 时长：1 分钟 ~ 15 分钟

---

### 4.3 内容获取 Skills

#### search → rednote-search
**功能**: 搜索小红书内容

**迁移方案**:
| 步骤 | 动作 | computer-mcp 工具 |
|------|------|------------------|
| 1 | 聚焦创作者平台 | `focus_window("小红书创作者中心")` |
| 2 | 导航到搜索页 | `hotkey("ctrl l")` → `type_text("www.xiaohongshu.com/search_result?keyword=关键词")` → `press_key("enter")` |
| 3 | 等待搜索结果 | `wait(3)` + `inspect_screen()` |
| 4 | 提取搜索结果 | AI 分析截图，提取笔记标题、作者、点赞数等 |
| 5 | 返回结果 | JSON 格式 |

**注意**: 搜索页可能需要登录才能查看完整信息

---

#### get-feed → rednote-get-feed
**功能**: 获取帖子详情

**迁移方案**:
| 步骤 | 动作 | computer-mcp 工具 |
|------|------|------------------|
| 1 | 导航到笔记页 | `type_text("www.xiaohongshu.com/explore/{noteId}")` → `press_key("enter")` |
| 2 | 等待加载 | `wait(3)` |
| 3 | 截图识别 | `inspect_screen()` |
| 4 | AI 提取信息 | 标题、内容、作者、点赞数、评论等 |

---

#### get-feeds → rednote-get-feeds
**功能**: 获取推荐列表

**迁移方案**:
| 步骤 | 动作 | computer-mcp 工具 |
|------|------|------------------|
| 1 | 导航到首页 | `type_text("www.xiaohongshu.com")` → `press_key("enter")` |
| 2 | 等待加载 | `wait(3)` |
| 3 | 截图识别 | `inspect_screen()` |
| 4 | AI 提取推荐列表 | 笔记标题、作者、摘要等 |
| 5 | 滚动加载更多 | `scroll()` 循环截图 |

---

#### get-profile → rednote-get-profile
**功能**: 获取用户主页

**迁移方案**:
| 步骤 | 动作 | computer-mcp 工具 |
|------|------|------------------|
| 1 | 导航到用户主页 | `type_text("www.xiaohongshu.com/user/profile/{userId}")` → `press_key("enter")` |
| 2 | 截图识别 | `inspect_screen()` |
| 3 | AI 提取信息 | 用户名、粉丝数、笔记列表等 |

---

### 4.4 互动功能 Skills

#### like → rednote-like
**功能**: 点赞/取消点赞

**迁移方案**:
| 步骤 | 动作 | computer-mcp 工具 |
|------|------|------------------|
| 1 | 导航到笔记页 | 同 get-feed |
| 2 | 找到点赞按钮 | `inspect_screen()` 找"点赞"/心形图标 |
| 3 | 点击点赞 | `click(x, y)` |
| 4 | 验证结果 | `inspect_screen()` 检查点赞状态 |

---

#### favorite → rednote-favorite
**功能**: 收藏/取消收藏

**迁移方案**:
| 步骤 | 动作 | computer-mcp 工具 |
|------|------|------------------|
| 1 | 导航到笔记页 | 同 get-feed |
| 2 | 找到收藏按钮 | `inspect_screen()` 找"收藏"/星形图标 |
| 3 | 点击收藏 | `click(x, y)` |
| 4 | 验证结果 | 截图检查 |

---

#### comment → rednote-comment
**功能**: 发表评论

**迁移方案**:
| 步骤 | 动作 | computer-mcp 工具 |
|------|------|------------------|
| 1 | 导航到笔记页 | 同 get-feed |
| 2 | 找到评论输入框 | `inspect_screen()` 找"发表评论" |
| 3 | 点击输入框 | `click(x, y)` |
| 4 | 输入评论内容 | `type_text("评论内容")` |
| 5 | 发送评论 | `inspect_screen()` 找"发送" → `click(x, y)` |
| 6 | 确认发送 | `confirm_action("确认发表评论？")` |

---

#### reply → rednote-reply
**功能**: 回复评论

**迁移方案**: 与 comment 类似，区别在于：
| 步骤 | 差异 | 说明 |
|------|------|------|
| 2 | 找到要回复的评论 | 滚动查找特定评论 |
| 3 | 点击"回复"按钮 | 评论下方的"回复"链接 |
| 4-6 | 同 comment | 输入并发送回复 |

---

## 5. 目录结构设计

### 5.1 目标结构

```
rednote/
├── README.md                       # 平台使用指南
├── session-rednote-migration.md    # 本迁移文档
│
├── lib/
│   ├── computer_mcp_client.py      # 复用 weibo 的客户端（或符号链接）
│   └── rednote_automation.py       # 小红书专用自动化封装
│
├── check-login/
│   ├── SKILL.md                    # ✅ 已更新为 computer-mcp
│   └── usage.md                    # 使用说明
│
├── get-qrcode/
│   ├── SKILL.md
│   └── usage.md
│
├── publish-note/
│   ├── SKILL.md
│   └── usage.md
│
├── publish-video/
│   ├── SKILL.md
│   └── usage.md
│
├── search/
│   ├── SKILL.md
│   └── usage.md
│
├── get-feed/
│   ├── SKILL.md
│   └── usage.md
│
├── get-feeds/
│   ├── SKILL.md
│   └── usage.md
│
├── get-profile/
│   ├── SKILL.md
│   └── usage.md
│
├── like/
│   ├── SKILL.md
│   └── usage.md
│
├── favorite/
│   ├── SKILL.md
│   └── usage.md
│
├── comment/
│   ├── SKILL.md
│   └── usage.md
│
├── reply/
│   ├── SKILL.md
│   └── usage.md
│
└── test/
    ├── pre-test-check.js           # 测试前环境检查
    ├── validate-selectors.js       # 选择器验证（改为验证 OCR 关键词）
    └── test-helper.js              # 测试辅助工具
```

### 5.2 文件变更说明

| 文件类型 | 变更 | 说明 |
|---------|------|------|
| `SKILL.md` | ✅ 重写 | 从 Playwright DOM 操作改为 computer-mcp 截图+多模态 AI 视觉理解流程 |
| `usage.md` | ✅ 更新 | 更新使用说明，反映新的技术方案 |
| `lib/rednote_automation.py` | ✅ 新增 | 小红书专用自动化封装 |
| `scripts/*.js` | ❌ 删除 | 不再需要 Node.js 脚本 |
| `lib/browser.js` | ❌ 废弃 | 不再使用 Playwright |
| `lib/cookie.js` | ❌ 废弃 | 复用系统浏览器 Cookie |

---

## 6. 关键技术问题

### 6.1 多模态 AI 视觉理解要点

多模态 AI 直接观察截图，识别界面状态和元素：
- **登录状态**: 直接看是否有用户头像/二维码
- **按钮位置**: 直接观察找到"发布"、"点赞"等按钮
- **内容提取**: 直接读取笔记标题、正文、作者等信息
- **表单填写**: 识别输入框位置并指导点击

| 界面元素 | 可能的关键词 | 匹配策略 | 出现页面 |
|---------|-------------|---------|---------|
| 登录二维码 | "扫码登录", "小红书 APP" | 模糊匹配 | 登录页 |
| 用户头像 | 用户昵称（右上角） | 精确匹配 | 所有页面 |
| 发布笔记 | "上传图文", "上传视频" | 模糊匹配 | 发布页 |
| 标题输入框 | "填写标题" | 前缀匹配 | 发布页 |
| 正文编辑器 | "填写正文", "正文" | 前缀匹配 | 发布页 |
| 话题标签 | "#", "添加话题" | 模糊匹配 | 发布页 |
| 发布按钮 | "发布", "立即发布" | 模糊匹配 | 发布页 |
| 搜索框 | "搜索" | 精确匹配 | 搜索页 |
| 点赞按钮 | "点赞", "赞" | 模糊匹配 | 笔记详情页 |
| 收藏按钮 | "收藏", "收藏过" | 模糊匹配 | 笔记详情页 |
| 评论输入框 | "说点什么", "发表评论" | 模糊匹配 | 笔记详情页 |
| 发送按钮 | "发送", "发布" | 模糊匹配 | 笔记详情页 |

### 6.2 窗口识别

**问题**: 多个浏览器标签页，如何准确聚焦创作者平台页面

**解决方案**:
- `focus_window` 支持模糊匹配（如 "小红书", "creator.xiaohongshu"）
- 若未找到，提示用户手动切换到创作者平台页面
- 优先使用 URL 识别（通过地址栏内容）

### 6.3 页面加载等待

**问题**: 点击后页面可能正在加载

**解决方案**:
- 每次操作后调用 `wait(1-3)`
- 循环 `inspect_screen` 检查目标元素是否出现
- 设置最大等待时间（如 10 秒），超时则报错

### 6.4 动态内容识别

**问题**: 小红书创作者平台页面元素位置可能随窗口大小变化

**解决方案**:
- 不硬编码坐标，每次都重新 `inspect_screen`
- 使用百分比坐标映射方案，适配不同分辨率
- 使用相对位置（如 "在标题输入框下方"）

### 6.5 文件上传

**问题**: 如何通过 computer-mcp 上传图片/视频

**解决方案**:
```python
# 1. 点击上传区域
self.mcp.click(upload_x, upload_y)
self.mcp.wait(1)

# 2. 在文件选择对话框中输入路径
self.mcp.type_text(image_path)
self.mcp.wait(0.5)

# 3. 按回车确认
self.mcp.press_key("enter")
self.mcp.wait(5)  # 等待上传完成
```

**注意**: 
- 文件选择对话框可能需要聚焦窗口
- 上传大文件需要更长等待时间
- 验证上传结果（检查缩略图是否出现）

### 6.6 验证码/风控处理

**问题**: 小红书可能触发验证码或风控

**解决方案**:
- 操作间添加随机延迟（1-3 秒）
- 模拟真实用户行为（滚动页面、停顿等）
- 如触发验证码，暂停自动化，提示用户手动处理
- 记录操作日志，便于追踪问题

---

## 7. 核心代码示例

### 7.1 RedNoteAutomation 类

```python
#!/usr/bin/env python3
"""
RedNote Automation - 小红书创作者平台自动化封装
基于 computer-mcp 实现
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../weibo/lib'))

from computer_mcp_client import ComputerMCPClient, WeiboAutomation
import pyautogui


class RedNoteAutomation:
    """小红书创作者平台自动化操作"""

    def __init__(self):
        self.mcp = ComputerMCPClient()
        self.window_found = False
        self.window_rect = None

    def find_or_open_creator(self) -> bool:
        """查找或打开小红书创作者平台窗口"""
        print("正在查找小红书创作者平台窗口...")

        # 尝试查找已打开的窗口
        titles = [
            "小红书创作者中心",
            "creator.xiaohongshu.com",
            "小红书 - ",
            "创作者中心",
        ]

        for title in titles:
            result = self.mcp.focus_window(title)
            if result.get("success"):
                print(f"✓ 找到小红书窗口 (标题: {title})")
                self.window_found = True
                return True

        # 未找到，打开浏览器
        print("未找到小红书窗口，正在打开浏览器...")
        result = self.mcp.open_browser("https://creator.xiaohongshu.com/")

        if not result.get("success"):
            print(f"✗ 打开浏览器失败: {result.get('error')}")
            return False

        # 等待页面加载
        print("等待页面加载...")
        self.mcp.wait(5)

        # 再次尝试聚焦
        for attempt in range(3):
            print(f"尝试聚焦 (第 {attempt + 1} 次)...")
            for title in titles:
                result = self.mcp.focus_window(title)
                if result.get("success"):
                    print(f"✓ 成功聚焦 (标题: {title})")
                    self.window_found = True
                    return True
            self.mcp.wait(2)

        print("✗ 无法聚焦小红书窗口")
        self.window_found = False
        return False

    def get_browser_window_rect(self) -> dict:
        """获取浏览器窗口的内容区域"""
        try:
            import win32gui
            import pyautogui

            def callback(hwnd, result):
                title = win32gui.GetWindowText(hwnd)
                if win32gui.IsWindowVisible(hwnd):
                    if any(keyword in title for keyword in ["小红书", "creator.xiaohongshu"]):
                        rect = win32gui.GetWindowRect(hwnd)
                        result.append({'hwnd': hwnd, 'rect': rect})
                return True

            windows = []
            win32gui.EnumWindows(callback, windows)

            if not windows:
                return None

            hwnd = windows[0]['hwnd']
            client_rect = win32gui.GetClientRect(hwnd)
            pt = win32gui.ClientToScreen(hwnd, (0, 0))

            return {
                "left": pt[0],
                "top": pt[1],
                "width": client_rect[2],
                "height": client_rect[3],
                "screen_resolution": pyautogui.size(),
            }
        except Exception as e:
            print(f"[debug] 获取窗口区域失败: {e}")
            return None

    def pct_to_screen_coords(self, pct_x: float, pct_y: float) -> tuple:
        """百分比坐标转屏幕绝对坐标"""
        if self.window_rect:
            wr = self.window_rect
            x = wr["left"] + int(wr["width"] * pct_x)
            y = wr["top"] + int(wr["height"] * pct_y)
            return (x, y)

        screen_w, screen_h = pyautogui.size()
        return (int(screen_w * pct_x), int(screen_h * pct_y))

    def check_login_status(self) -> dict:
        """检查登录状态，返回截图供 AI 分析"""
        if not self.window_found:
            if not self.find_or_open_creator():
                return {"loggedIn": None, "error": "无法打开创作者平台窗口"}

        result = self.mcp.inspect_screen()

        if not result.get("success"):
            return {"loggedIn": None, "error": "截图失败"}

        return {
            "loggedIn": None,  # 由 AI 分析截图判断
            "screenshot_path": result.get("screenshot_path"),
        }

    def navigate_to(self, url: str) -> bool:
        """导航到指定 URL"""
        # Ctrl+L 聚焦地址栏
        self.mcp.hotkey(["ctrl", "l"])
        self.mcp.wait(0.5)

        # 输入 URL
        self.mcp.hotkey(["ctrl", "a"])  # 全选
        self.mcp.wait(0.3)
        self.mcp.type_text(url)
        self.mcp.wait(0.3)

        # 回车
        self.mcp.press_key("enter")
        self.mcp.wait(3)

        return True

    def publish_note(self, title: str, content: str, images: list, tags: list = None) -> dict:
        """发布图文笔记"""
        import pyperclip

        # 1. 检查登录状态
        login_status = self.check_login_status()
        if not login_status.get("screenshot_path"):
            return {"success": False, "error": "登录状态检查失败"}

        # 2. 导航到发布页
        print("导航到发布页...")
        self.navigate_to("https://creator.xiaohongshu.com/publish/publish")
        self.mcp.wait(3)

        # 3. 截图识别页面状态
        result = self.mcp.inspect_screen()
        print(f"页面截图: {result.get('screenshot_path')}")

        # AI 需要分析截图，找到"上传图文"按钮并点击
        # 这里返回截图，由 AI 决定下一步操作
        return {
            "success": True,
            "message": "已到达发布页，请 AI 分析截图并指导操作",
            "screenshot_path": result.get("screenshot_path"),
            "next_steps": [
                "识别'上传图文'按钮并点击",
                "上传图片文件",
                "填写标题和正文",
                "添加话题标签",
                "点击发布按钮"
            ]
        }


if __name__ == "__main__":
    rednote = RedNoteAutomation()
    print("正在检查登录状态...")
    status = rednote.check_login_status()
    print(f"登录状态: {status}")
```

---

## 8. 依赖与配置

### 8.1 必需依赖

**Python 包**:
```bash
pip install pyautogui pyperclip pywin32 pillow
```

**MCP 服务器**:
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

### 8.2 系统要求
- Windows 10/11
- Edge 或 Chrome 浏览器
- 浏览器已登录 creator.xiaohongshu.com

### 8.3 环境变量（可选）
```bash
# 数据存储路径（截图、日志等）
REDNOTE_DATA_PATH=D:\08_tmp\02_media\power-media\rednote\data

# 截图保存路径
REDNOTE_SCREENSHOT_PATH=D:\08_tmp\02_media\power-media\computer-mcp\screenshots
```

---

## 9. 验收标准

### 9.1 功能验收

| Skill | 验收标准 |
|-------|---------|
| check-login | ✅ 能正确识别登录/未登录状态 |
| get-qrcode | ✅ 能显示登录二维码并等待扫码 |
| publish-note | ✅ 能成功发布图文笔记 |
| publish-video | ✅ 能成功发布视频笔记 |
| search | ✅ 能搜索内容并返回结果 |
| get-feed | ✅ 能获取笔记详情 |
| get-feeds | ✅ 能获取推荐列表 |
| get-profile | ✅ 能获取用户主页信息 |
| like | ✅ 能点赞/取消点赞 |
| favorite | ✅ 能收藏/取消收藏 |
| comment | ✅ 能发表评论 |
| reply | ✅ 能回复评论 |

### 9.2 稳定性验收

- [ ] 连续执行 5 次发布操作，成功率 ≥ 80%
- [ ] 登录状态检查响应时间 ≤ 5 秒
- [ ] 发布操作总耗时 ≤ 60 秒
- [ ] 窗口查找失败时能自动打开浏览器

### 9.3 安全验收

- [ ] 所有发布操作都经过 `confirm_action` 确认
- [ ] 敏感操作有明确日志记录
- [ ] 错误时有清晰的提示信息
- [ ] 不保存敏感信息（Cookie、密码等）

---

## 10. 迁移计划

### Phase 1: 基础设施 + 认证（1-2 天）
- [ ] 创建 `lib/rednote_automation.py`
- [ ] 迁移 `check-login` SKILL.md
- [ ] 迁移 `get-qrcode` SKILL.md
- [ ] 测试登录流程

### Phase 2: 内容发布（2-3 天）
- [ ] 迁移 `publish-note` SKILL.md
- [ ] 迁移 `publish-video` SKILL.md
- [ ] 完善错误处理
- [ ] 测试发布流程

### Phase 3: 内容获取（1-2 天）
- [ ] 迁移 `search` SKILL.md
- [ ] 迁移 `get-feed` SKILL.md
- [ ] 迁移 `get-feeds` SKILL.md
- [ ] 迁移 `get-profile` SKILL.md

### Phase 4: 互动功能（1-2 天）
- [ ] 迁移 `like` SKILL.md
- [ ] 迁移 `favorite` SKILL.md
- [ ] 迁移 `comment` SKILL.md
- [ ] 迁移 `reply` SKILL.md

### Phase 5: 清理与文档（1 天）
- [ ] 删除旧 Playwright 代码（`lib/browser.js`, `lib/cookie.js`）
- [ ] 更新 README 和文档
- [ ] 集成测试
- [ ] 编写使用指南

---

## 11. 风险评估

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|---------|
| 多模态 AI 理解不准 | 低 | 高 | 提供更清晰的截图，重试截图，人工 fallback |
| 页面改版 | 中 | 高 | 多模态 AI 适应性强，定期验证 |
| 窗口焦点丢失 | 低 | 中 | 每次操作前重新 focus_window |
| 操作超时 | 低 | 低 | 设置合理超时时间，友好错误提示 |
| 验证码/风控 | 中 | 高 | 随机延迟、模拟真实用户行为、人工介入 |
| 文件上传失败 | 低 | 中 | 重试机制、检查文件路径、验证上传结果 |

---

## 附录

### A. 小红书创作者平台关键 URL

| 页面 | URL |
|------|-----|
| 创作者中心首页 | `https://creator.xiaohongshu.com/` |
| 发布笔记页 | `https://creator.xiaohongshu.com/publish/publish` |
| 数据看板 | `https://creator.xiaohongshu.com/data` |
| 笔记管理 | `https://creator.xiaohongshu.com/manage/notes` |

### B. 平台限制

| 限制项 | 数值 |
|--------|------|
| 标题长度 | ≤ 20 字 |
| 正文长度 | ≤ 1000 字 |
| 图片数量 | ≤ 18 张 |
| 视频大小 | ≤ 2GB |
| 视频时长 | 1 分钟 ~ 15 分钟 |
| 话题标签 | ≤ 10 个 |
| 日发布量 | 约 50 篇 |

### C. 与 Weibo 实现的区别

| 维度 | Weibo | RedNote |
|------|-------|---------|
| 目标平台 | weibo.com | creator.xiaohongshu.com |
| 内容类型 | 短文本（140 字） | 图文/视频笔记 |
| 发布流程 | 简单（输入+发送） | 复杂（多步骤表单） |
| 文件上传 | 图片 | 图片/视频 |
| 表单字段 | 少 | 多（标题、正文、标签等） |
| 交互复杂度 | 低 | 高 |

---

## 变更日志

| 日期 | 变更内容 |
|------|----------|
| 2026-04-12 | 创建文档，完成迁移规格设计 |
| 2026-04-12 | 参考 weibo 迁移经验和技术方案 |
| 2026-04-12 | 完成所有 12 个 Skills 的迁移方案设计 |

---

**评审记录**

| 日期 | 评审人 | 意见 | 状态 |
|------|--------|------|------|
| 2026-04-12 | - | 初稿创建 | 📝 Draft |
