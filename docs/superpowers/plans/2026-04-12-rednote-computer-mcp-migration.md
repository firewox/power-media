# RedNote Skills 迁移至 computer-mcp 实施计划

**日期**: 2026-04-12
**参考规格**: [迁移规格书](../specs/2026-04-12-rednote-computer-mcp-migration.md)
**参考实现**: [weibo 实现](../../../weibo/)

---

## 〇、前置准备

### 0.1 确认当前状态

```bash
# 1. 检查当前分支
git branch --show-current
# 预期: rednote-dev 或创建新分支 rednote-computer-mcp

# 2. 查看当前 rednote 目录结构
tree rednote /F
# 注意: Windows 使用 tree /F，Linux/Mac 使用 tree

# 3. 检查 computer-mcp 是否可用
python computer-mcp/server.py --help

# 4. 检查 weibo/lib/computer_mcp_client.py 是否存在
ls weibo/lib/computer_mcp_client.py
```

### 0.2 创建开发分支

```bash
# 如果 rednote-dev 分支已存在
git checkout rednote-dev

# 或者创建新分支
git checkout -b rednote-computer-mcp

# 查看当前状态
git status
```

### 0.3 备份现有代码

```bash
# 备份旧的 Playwright 实现（以防需要参考）
cp -r rednote/lib rednote/lib.backup
cp -r rednote/test rednote/test.backup
```

---

## 一、Phase 1: 基础设施 + 认证

**目标**: 建立基础架构，实现登录相关 skills
**预计时间**: 1-2 天

### Task 1.1: 创建核心自动化库

#### 1.1.1 复用 computer_mcp_client.py

**方案 A**: 符号链接（推荐，避免代码重复）
```bash
# 在 rednote/lib 下创建符号链接指向 weibo/lib
cd rednote/lib
mklink computer_mcp_client.py ..\..\weibo\lib\computer_mcp_client.py
# 注意: Windows 使用 mklink，需要管理员权限
```

**方案 B**: 复制到项目级 lib 目录
```bash
# 创建项目级 lib 目录
mkdir lib

# 复制客户端库
cp weibo/lib/computer_mcp_client.py lib/

# 更新所有引用
# rednote 和 weibo 都从 lib/ 导入
```

**推荐**: 方案 A（符号链接），保持单一数据源

#### 1.1.2 创建 rednote_automation.py

**文件**: `rednote/lib/rednote_automation.py`

```python
#!/usr/bin/env python3
"""
RedNote Automation - 小红书创作者平台自动化封装
基于 computer-mcp 实现
"""
import sys
import os

# 添加 computer_mcp_client 到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from computer_mcp_client import ComputerMCPClient
import pyautogui


class RedNoteAutomation:
    """小红书创作者平台自动化操作"""

    CREATOR_URL = "https://creator.xiaohongshu.com/"
    PUBLISH_URL = "https://creator.xiaohongshu.com/publish/publish"
    
    WINDOW_TITLES = [
        "小红书创作者中心",
        "creator.xiaohongshu.com",
        "小红书 - ",
        "创作者中心",
    ]

    def __init__(self):
        self.mcp = ComputerMCPClient()
        self.window_found = False
        self.window_rect = None

    def find_or_open_creator(self) -> bool:
        """查找或打开小红书创作者平台窗口"""
        print("正在查找小红书创作者平台窗口...")

        for title in self.WINDOW_TITLES:
            result = self.mcp.focus_window(title)
            if result.get("success"):
                print(f"✓ 找到小红书窗口 (标题: {title})")
                self.window_found = True
                return True

        # 未找到，打开浏览器
        print("未找到小红书窗口，正在打开浏览器...")
        result = self.mcp.open_browser(self.CREATOR_URL)

        if not result.get("success"):
            return False

        print("等待页面加载...")
        self.mcp.wait(5)

        for attempt in range(3):
            print(f"尝试聚焦 (第 {attempt + 1} 次)...")
            for title in self.WINDOW_TITLES:
                result = self.mcp.focus_window(title)
                if result.get("success"):
                    self.window_found = True
                    return True
            self.mcp.wait(2)

        return False

    def get_browser_window_rect(self) -> dict:
        """获取浏览器窗口的内容区域"""
        try:
            import win32gui

            def callback(hwnd, result):
                title = win32gui.GetWindowText(hwnd)
                if win32gui.IsWindowVisible(hwnd):
                    if any(kw in title for kw in ["小红书", "creator.xiaohongshu"]):
                        client_rect = win32gui.GetClientRect(hwnd)
                        pt = win32gui.ClientToScreen(hwnd, (0, 0))
                        result.append({
                            "left": pt[0],
                            "top": pt[1],
                            "width": client_rect[2],
                            "height": client_rect[3],
                        })
                return True

            windows = []
            win32gui.EnumWindows(callback, windows)

            if not windows:
                return None

            self.window_rect = windows[0]
            return self.window_rect

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
            "loggedIn": None,
            "screenshot_path": result.get("screenshot_path"),
        }

    def navigate_to(self, url: str) -> bool:
        """导航到指定 URL"""
        self.mcp.hotkey(["ctrl", "l"])
        self.mcp.wait(0.5)
        self.mcp.hotkey(["ctrl", "a"])
        self.mcp.wait(0.3)
        self.mcp.type_text(url)
        self.mcp.wait(0.3)
        self.mcp.press_key("enter")
        self.mcp.wait(3)
        return True


if __name__ == "__main__":
    rednote = RedNoteAutomation()
    print("正在检查登录状态...")
    status = rednote.check_login_status()
    print(f"登录状态: {status}")
```

**验证**:
```bash
# 测试运行
cd rednote/lib
python rednote_automation.py

# 预期输出:
# 正在查找小红书创作者平台窗口...
# ✓ 找到小红书窗口 (标题: xxx)
# 正在检查登录状态...
# 登录状态: {'loggedIn': None, 'screenshot_path': '...'}
```

---

### Task 1.2: 迁移 check-login

#### 1.2.1 更新 SKILL.md

**文件**: `rednote/check-login/SKILL.md`

```markdown
---
name: rednote-check-login
description: |
  检查小红书创作者平台登录状态。

  触发条件：
  - "检查小红书登录状态"
  - "小红书登录了吗"
  - "查看小红书是否登录"
  - 任何涉及检查小红书账号登录状态的请求

  工作流程：
  1. 聚焦/打开创作者平台窗口
  2. 截图识别页面状态
  3. AI 分析截图判断登录状态

  依赖：
  - computer-mcp (inspect_screen, focus_window)
  - 浏览器已打开 creator.xiaohongshu.com 页面

compatibility: |
  - computer-mcp >= 1.0
  - Windows 10/11
  - Edge / Chrome 浏览器
  - Python 3.8+
---

# 检查小红书登录状态

## 工作流程

### Step 1: 聚焦创作者平台窗口

调用 computer-mcp 聚焦窗口：
```json
{"tool": "computer-mcp/focus_window", "params": {"title": "小红书创作者中心"}}
```

或使用 `rednote_automation.find_or_open_creator()` 自动查找/打开。

### Step 2: 截图识别

```json
{"tool": "computer-mcp/inspect_screen", "params": {}}
```

返回截图路径，供多模态 AI 分析。

### Step 3: AI 分析登录状态

AI 分析截图，判断：
- **已登录**: 检测到右上角用户头像/昵称
- **未登录**: 检测到登录二维码/登录按钮

## 输入参数

无必需参数。

## 输出结果

**已登录时**:
```json
{
  "success": true,
  "loggedIn": true,
  "screenshot_path": "D:\\...\\rednote_shot_xxx.png"
}
```

**未登录时**:
```json
{
  "success": true,
  "loggedIn": false,
  "screenshot_path": "D:\\...\\rednote_shot_xxx.png",
  "message": "未登录，请扫码登录"
}
```

## 使用示例

```
用户：检查小红书登录状态
结果：已登录

用户：小红书登录了吗
结果：未登录，请执行 rednote-get-qrcode 获取登录二维码
```

## 注意事项

1. 需要浏览器已打开创作者平台页面
2. Cookie 有效期通常为几天到几周
3. 同一账号只能在一个浏览器实例中保持登录状态
```

#### 1.2.2 创建测试脚本

**文件**: `rednote/check-login/scripts/check_login.py`

```python
#!/usr/bin/env python3
"""
检查小红书创作者平台登录状态
"""
import sys
import os
import json

# 添加 lib 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from rednote_automation import RedNoteAutomation


def main():
    """主函数"""
    print("🔍 检查小红书创作者平台登录状态...\n")

    automation = RedNoteAutomation()

    # 查找/打开窗口
    if not automation.find_or_open_creator():
        print("✗ 无法打开创作者平台窗口")
        print(json.dumps({
            "success": False,
            "error": "无法打开创作者平台窗口"
        }, ensure_ascii=False))
        return

    # 检查登录状态
    result = automation.check_login_status()

    print(f"\n截图路径: {result.get('screenshot_path')}")
    print("请 AI 分析截图判断登录状态")

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```

**验证**:
```bash
cd rednote/check-login/scripts
python check_login.py
```

---

### Task 1.3: 迁移 get-qrcode

#### 1.3.1 更新 SKILL.md

**文件**: `rednote/get-qrcode/SKILL.md`

```markdown
---
name: rednote-get-qrcode
description: |
  获取小红书创作者平台登录二维码。

  触发条件：
  - "获取小红书登录二维码"
  - "小红书扫码登录"
  - "获取登录二维码"

  工作流程：
  1. 聚焦/打开创作者平台
  2. 检查是否已登录
  3. 如未登录，截图显示二维码
  4. 循环检测登录状态（最多 2 分钟）

compatibility: |
  - computer-mcp >= 1.0
  - Windows 10/11
---

# 获取小红书登录二维码

## 工作流程

### Step 1: 聚焦创作者平台

调用 `find_or_open_creator()` 确保窗口已打开。

### Step 2: 检查是否已登录

调用 `inspect_screen()` 截图，AI 分析：
- 已登录 → 提示用户已登录，无需扫码
- 未登录 → 继续下一步

### Step 3: 截图显示二维码

```json
{"tool": "computer-mcp/inspect_screen", "params": {}}
```

返回截图，二维码应显示在页面中央。

### Step 4: 等待用户扫码

循环检测登录状态（每 3 秒一次，最多 40 次 = 2 分钟）：
1. `inspect_screen()` 截图
2. AI 分析是否已登录
3. 如已登录，退出循环
4. 如超时，提示刷新页面重新获取二维码

## 输出结果

```json
{
  "success": true,
  "qrcode_path": "D:\\...\\rednote_qr_xxx.png",
  "message": "请使用小红书 APP 扫码登录",
  "timeout": 120
}
```

## 注意事项

1. 二维码有效期约 2 分钟
2. 超时需刷新页面重新获取
3. 需要小红书 APP 扫码
```

---

### Task 1.4: Phase 1 测试与验证

#### 1.4.1 环境检查

```bash
# 1. 检查依赖
python -c "import pyautogui; print('pyautogui OK')"
python -c "import pyperclip; print('pyperclip OK')"
python -c "import win32gui; print('pywin32 OK')"

# 2. 检查 computer-mcp
python computer-mcp/server.py --help

# 3. 检查浏览器
# 手动确认: Edge/Chrome 已打开 creator.xiaohongshu.com
```

#### 1.4.2 功能测试

```bash
# 1. 测试 check-login
cd rednote/check-login/scripts
python check_login.py

# 2. 测试 get-qrcode（如未登录）
cd rednote/get-qrcode/scripts
python get_qrcode.py

# 3. 截图验证
# 检查截图是否正确显示登录页面/二维码
```

#### 1.4.3 验收标准

- [ ] `find_or_open_creator()` 能正确查找/打开窗口
- [ ] `check_login_status()` 能返回截图
- [ ] 截图清晰，能看出登录状态
- [ ] AI 能正确分析截图判断登录状态

---

## 二、Phase 2: 内容发布

**目标**: 实现图文/视频笔记发布功能
**预计时间**: 2-3 天

### Task 2.1: 迁移 publish-note

#### 2.1.1 更新 SKILL.md

**文件**: `rednote/publish-note/SKILL.md`

关键工作流程：

```yaml
## 工作流程（computer-mcp）

### Step 1: 前置检查
调用 `rednote-check-login` 确认已登录。

### Step 2: 导航到发布页
```json
{
  "tool": "computer-mcp/hotkey",
  "params": {"keys": ["ctrl", "l"]}
}
```
然后输入 URL: `creator.xiaohongshu.com/publish/publish`

### Step 3: 选择"上传图文"
`inspect_screen()` 识别"上传图文"按钮 → `click(x, y)`

### Step 4: 上传图片
1. `inspect_screen()` 找上传区域
2. `click(x, y)` 触发文件选择对话框
3. `type_text("图片路径")` 输入路径
4. `press_key("enter")` 确认
5. `wait(5)` 等待上传

### Step 5: 填写标题
1. `inspect_screen()` 找标题输入框
2. `click(x, y)` 聚焦
3. `type_text("标题内容")`

### Step 6: 填写正文
1. `inspect_screen()` 找正文编辑器
2. `click(x, y)` 聚焦
3. `type_text("正文内容")`

### Step 7: 添加话题标签
在正文中输入 `#话题` 格式

### Step 8: 点击发布
1. `inspect_screen()` 找"发布"按钮
2. `click(x, y)`
3. `confirm_action("确认发布小红书笔记？")`

### Step 9: 验证结果
`inspect_screen()` 检查"发布成功"提示
```

#### 2.1.2 创建辅助脚本

**文件**: `rednote/publish-note/scripts/publish_note.py`

```python
#!/usr/bin/env python3
"""
发布小红书图文笔记
"""
import sys
import os
import json
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lib'))
from rednote_automation import RedNoteAutomation


def validate_inputs(title, content, images, tags=None):
    """验证输入参数"""
    errors = []

    if len(title) > 20:
        errors.append(f"标题过长: {len(title)} 字（最多 20 字）")

    if len(content) > 1000:
        errors.append(f"正文过长: {len(content)} 字（最多 1000 字）")

    if len(images) > 18:
        errors.append(f"图片过多: {len(images)} 张（最多 18 张）")

    if tags and len(tags) > 10:
        errors.append(f"标签过多: {len(tags)} 个（最多 10 个）")

    for img_path in images:
        if not os.path.exists(img_path):
            errors.append(f"图片不存在: {img_path}")

    return errors


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='发布小红书图文笔记')
    parser.add_argument('--title', required=True, help='笔记标题（最多 20 字）')
    parser.add_argument('--content', required=True, help='笔记正文（最多 1000 字）')
    parser.add_argument('--images', required=True, nargs='+', help='图片路径列表')
    parser.add_argument('--tags', nargs='+', help='话题标签列表')

    args = parser.parse_args()

    # 验证输入
    errors = validate_inputs(args.title, args.content, args.images, args.tags)
    if errors:
        print("❌ 参数验证失败:")
        for error in errors:
            print(f"  - {error}")
        print(json.dumps({"success": False, "errors": errors}, ensure_ascii=False))
        return

    print(f"📝 发布小红书图文笔记")
    print(f"标题: {args.title}")
    print(f"图片: {len(args.images)} 张\n")

    automation = RedNoteAutomation()

    # 1. 检查登录状态
    print("1. 检查登录状态...")
    login_status = automation.check_login_status()
    if not login_status.get("screenshot_path"):
        print("✗ 登录状态检查失败")
        return

    # 2. 导航到发布页
    print("\n2. 导航到发布页...")
    automation.navigate_to(automation.PUBLISH_URL)
    automation.mcp.wait(3)

    # 3. 截图识别页面
    result = automation.mcp.inspect_screen()
    print(f"页面截图: {result.get('screenshot_path')}")

    # 返回截图，由 AI 指导后续操作
    print("\n3. 请 AI 分析截图并指导操作:")
    print("  - 识别'上传图文'按钮并点击")
    print("  - 上传图片文件")
    print("  - 填写标题和正文")
    print("  - 添加话题标签")
    print("  - 点击发布按钮")

    print(json.dumps({
        "success": True,
        "message": "已到达发布页，请 AI 分析截图并指导操作",
        "screenshot_path": result.get("screenshot_path"),
        "params": {
            "title": args.title,
            "content": args.content,
            "images": args.images,
            "tags": args.tags
        }
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```

**验证**:
```bash
cd rednote/publish-note/scripts
python publish_note.py \
  --title "测试标题" \
  --content "测试内容" \
  --images "test/image1.jpg" "test/image2.jpg" \
  --tags "#测试" "#demo"
```

---

### Task 2.2: 迁移 publish-video

与 publish-note 类似，区别在于：
- 选择"上传视频"而非"上传图文"
- 上传视频文件（MP4 格式）
- 需要设置封面和标题

**文件**: `rednote/publish-video/SKILL.md`
**文件**: `rednote/publish-video/scripts/publish_video.py`（结构类似 publish-note）

---

### Task 2.3: Phase 2 测试

```bash
# 1. 准备测试素材
mkdir -p rednote/test-data
# 放入 2-3 张测试图片

# 2. 测试发布流程（需人工监督）
cd rednote/publish-note/scripts
python publish_note.py \
  --title "测试笔记" \
  --content "这是测试内容 #测试" \
  --images "../../test-data/test1.jpg"

# 3. 验证发布结果
# 手动检查创作者平台是否成功发布
```

**验收标准**:
- [ ] 能导航到发布页
- [ ] 能上传图片
- [ ] 能填写标题和正文
- [ ] 能添加话题标签
- [ ] 发布成功（需人工确认）
- [ ] 错误处理正确（参数验证、登录检查等）

---

## 三、Phase 3: 内容获取

**目标**: 实现搜索、获取内容等功能
**预计时间**: 1-2 天

### Task 3.1: 迁移 search

**文件**: `rednote/search/SKILL.md`

工作流程：
1. 导航到搜索页: `www.xiaohongshu.com/search_result?keyword=关键词`
2. 等待加载: `wait(3)`
3. 截图识别: `inspect_screen()`
4. AI 提取搜索结果
5. 返回 JSON 结果

---

### Task 3.2: 迁移 get-feed, get-feeds, get-profile

这三个 skill 类似，都是：
1. 导航到指定页面
2. 截图识别
3. AI 提取信息
4. 返回结果

**文件**:
- `rednote/get-feed/SKILL.md`
- `rednote/get-feeds/SKILL.md`
- `rednote/get-profile/SKILL.md`

---

## 四、Phase 4: 互动功能

**目标**: 实现点赞、收藏、评论等功能
**预计时间**: 1-2 天

### Task 4.1: 迁移 like, favorite

工作流程：
1. 导航到笔记详情页
2. 截图识别按钮位置
3. 点击操作
4. 验证结果

---

### Task 4.2: 迁移 comment, reply

工作流程：
1. 导航到笔记详情页
2. 找到评论输入框
3. 输入评论内容
4. 点击发送
5. 确认操作（`confirm_action`）

---

## 五、Phase 5: 清理与文档

**目标**: 删除旧代码，更新文档
**预计时间**: 1 天

### Task 5.1: 删除旧 Playwright 代码

```bash
# 删除旧库文件
rm -rf rednote/lib.backup  # 如果不再需要

# 注意: 不要删除 lib/rednote_automation.py 和 lib/computer_mcp_client.py
```

### Task 5.2: 更新文档

- [ ] 更新 `rednote/README.md`
- [ ] 更新 `rednote/session-rednote.md`
- [ ] 更新 `docs/roadmap.md`
- [ ] 更新 `AGENTS.md` 中的平台状态表

### Task 5.3: 集成测试

```bash
# 运行完整测试流程
# 1. 检查登录
# 2. 搜索内容
# 3. 发布笔记
# 4. 互动功能
```

---

## 六、文件结构变化

### 6.1 新增文件

```
rednote/
├── lib/
│   ├── computer_mcp_client.py      # 符号链接或复制自 weibo
│   └── rednote_automation.py       # ✅ 新增
│
├── check-login/
│   └── scripts/
│       └── check_login.py          # ✅ 新增
│
├── get-qrcode/
│   └── scripts/
│       └── get_qrcode.py           # ✅ 新增
│
├── publish-note/
│   └── scripts/
│       └── publish_note.py         # ✅ 新增
│
├── publish-video/
│   └── scripts/
│       └── publish_video.py        # ✅ 新增
│
└── test-data/                      # ✅ 新增（测试用）
    └── test1.jpg
```

### 6.2 更新文件

- `rednote/*/SKILL.md` - 所有 skill 的定义文件（12个）
- `rednote/*/usage.md` - 使用说明（12个）

### 6.3 废弃文件（不删除，仅标记）

- `rednote/lib/browser.js` - ❌ 不再使用
- `rednote/lib/cookie.js` - ❌ 不再使用
- `rednote/lib/system-browser.js` - ❌ 不再使用
- `rednote/test/*.js` - ❌ 旧测试文件

---

## 七、Git 提交计划

### 7.1 提交策略

```bash
# Phase 1 完成
git add rednote/lib/
git add rednote/check-login/
git add rednote/get-qrcode/
git commit -m "Add: Phase 1 - 基础设施和认证 skills 迁移至 computer-mcp"

# Phase 2 完成
git add rednote/publish-note/
git add rednote/publish-video/
git commit -m "Add: Phase 2 - 内容发布 skills 迁移至 computer-mcp"

# Phase 3 完成
git add rednote/search/
git add rednote/get-feed/
git add rednote/get-feeds/
git add rednote/get-profile/
git commit -m "Add: Phase 3 - 内容获取 skills 迁移至 computer-mcp"

# Phase 4 完成
git add rednote/like/
git add rednote/favorite/
git add rednote/comment/
git add rednote/reply/
git commit -m "Add: Phase 4 - 互动功能 skills 迁移至 computer-mcp"

# Phase 5 完成
git add rednote/README.md
git add rednote/session-rednote.md
git add docs/
git commit -m "Update: Phase 5 - 清理旧代码，更新文档"
```

### 7.2 提交前检查

```bash
# 1. 检查当前分支
git branch --show-current

# 2. 查看变更文件
git status

# 3. 查看变更内容
git diff

# 4. 运行测试
python rednote/check-login/scripts/check_login.py

# 5. 提交
git commit -m "..."
```

---

## 八、验收检查清单

### 8.1 功能验收

| Skill | 验收方法 | 状态 |
|-------|---------|------|
| check-login | 运行脚本，检查截图 | ☐ |
| get-qrcode | 获取二维码，扫码登录 | ☐ |
| publish-note | 发布测试笔记 | ☐ |
| publish-video | 发布测试视频 | ☐ |
| search | 搜索关键词，检查结果 | ☐ |
| get-feed | 获取笔记详情 | ☐ |
| get-feeds | 获取推荐列表 | ☐ |
| get-profile | 获取用户主页 | ☐ |
| like | 点赞测试 | ☐ |
| favorite | 收藏测试 | ☐ |
| comment | 评论测试 | ☐ |
| reply | 回复测试 | ☐ |

### 8.2 稳定性验收

- [ ] 连续执行 5 次发布操作，成功率 ≥ 80%
- [ ] 登录状态检查响应时间 ≤ 5 秒
- [ ] 发布操作总耗时 ≤ 60 秒
- [ ] 窗口查找失败时能自动打开浏览器

### 8.3 安全验收

- [ ] 所有发布操作都经过 `confirm_action` 确认
- [ ] 敏感操作有明确日志记录
- [ ] 错误时有清晰的提示信息
- [ ] 不保存敏感信息（Cookie、密码等）

---

## 九、风险与应对

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|---------|
| OCR 识别不准 | 中 | 高 | 使用多关键词匹配、人工 fallback |
| 页面改版 | 中 | 高 | 更新 SKILL.md 中的关键词映射 |
| 窗口找不到 | 低 | 中 | 提示用户手动打开浏览器 |
| 上传失败 | 低 | 中 | 重试机制、检查文件路径 |
| 触发验证码 | 中 | 高 | 暂停自动化，提示人工处理 |

---

## 十、时间线

| 阶段 | 任务 | 预计时间 | 完成日期 |
|------|------|---------|---------|
| Phase 1 | 基础设施+认证 | 1-2 天 | 2026-04-13/14 |
| Phase 2 | 内容发布 | 2-3 天 | 2026-04-15/16 |
| Phase 3 | 内容获取 | 1-2 天 | 2026-04-17 |
| Phase 4 | 互动功能 | 1-2 天 | 2026-04-18 |
| Phase 5 | 清理与文档 | 1 天 | 2026-04-19 |
| **总计** | | **6-9 天** | **2026-04-19** |

---

*实施计划创建时间: 2026-04-12*
*下一步: 开始执行 Phase 1 - Task 1.1*
