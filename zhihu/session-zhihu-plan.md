# 知乎发布功能技术方案

> 创建时间: 2026-03-26
> 状态: 方案确定，待实现

---

## 一、需求概述

实现 AI 自动发布内容到知乎的功能，包括：
- 发布文章到知乎专栏
- 回答知乎问题
- 发布想法
- 图片上传

---

## 二、核心发现

### 2.1 知乎官方 API 情况

| 项目 | 状态 | 说明 |
|------|------|------|
| 知乎开放平台 | ❌ 不存在 | `dev.zhihu.com` 无法访问，DNS 解析失败 |
| 官方内容发布 API | ❌ 无公开接口 | 知乎没有公开的内容发布 API |
| 知乎 API v4 | ⚠️ 仅限内部使用 | 存在但不对第三方开放，测试返回权限错误 |

**结论**：知乎没有官方的内容发布 API，所有第三方实现都是通过非官方方式。

### 2.2 可行方案

| 方案 | 合规性 | 稳定性 | 开发难度 | 推荐度 |
|------|--------|--------|----------|--------|
| Playwright + CDP 连接 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 原生 CDP | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Selenium | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| 逆向 API | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |

---

## 三、Chrome DevTools Protocol (CDP) 技术分析

### 3.1 什么是 CDP

**定义**：CDP 是 Chrome 浏览器原生的调试协议，通过 WebSocket 连接实现对浏览器的底层控制。

**架构**：
```
┌─────────────┐
│   你的代码    │
└──────┬──────┘
       │ WebSocket
┌──────▼──────────────────────┐
│  Chrome DevTools Protocol   │
│  (localhost:9222)           │
└──────┬──────────────────────┘
       │
┌──────▼──────────┐
│  Chrome Browser │
│  (CDP Server)   │
└─────────────────┘
```

### 3.2 CDP vs Playwright 关系

```
Playwright 架构：
┌──────────────┐    WebSocket    ┌──────────────┐    CDP    ┌──────────┐
│ Python/JS    │ ───────────────▶│ Node.js      │ ─────────▶│ Chrome   │
│ 客户端代码   │                  │ 中继服务器    │           │ 浏览器   │
└──────────────┘                  └──────────────┘           └──────────┘

直接使用 CDP：
┌──────────────┐    WebSocket (CDP)    ┌──────────┐
│ Python/JS    │ ─────────────────────▶│ Chrome   │
│ 客户端代码   │                        │ 浏览器   │
└──────────────┘                        └──────────┘
```

### 3.3 CDP 主要域

| 域 | 功能 |
|---|------|
| Runtime | JavaScript 执行环境 |
| Network | 网络请求监控和控制 |
| DOM | 文档对象模型操作 |
| Page | 页面生命周期管理 |
| Fetch | 请求拦截和修改 |
| Input | 用户输入模拟 |
| Storage | Cookie/LocalStorage 管理 |

### 3.4 Browser-Use 从 Playwright 转向原生 CDP 的原因

| 维度 | Playwright | 原生 CDP |
|------|------------|----------|
| 延迟 | 双层 RPC（多一次网络跳转） | 单层直连 |
| 元素提取速度 | 较慢 | 提升 3-5 倍 |
| 截图速度 | 较慢 | 大幅提升 |
| 跨域 iframe | 支持受限 | 完全支持 |
| 崩溃处理 | 部分场景卡死 | 可自定义恢复逻辑 |

---

## 四、推荐方案

### 4.1 方案选择：Playwright + CDP 连接

**理由**：
1. Playwright 底层就是 CDP，性能接近原生
2. 高层 API 开发效率高（代码量减少 3 倍）
3. 需要底层控制时可直接访问 CDP Session
4. 自动处理等待、重试、错误
5. 社区成熟，文档完善

### 4.2 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Power Media Skill 层                      │
│                  (zhihu-publisher Skill)                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Playwright 层                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  页面操作   │  │  CDP Session│  │  Cookie管理 │         │
│  │  (高级API)  │  │  (底层控制)  │  │  (持久化)   │         │
└─────────────────────────┬───────────────────────────────────┘
                          │ WebSocket
┌─────────────────────────▼───────────────────────────────────┐
│              Chrome Browser (CDP Server)                     │
│                 localhost:9222                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 五、实现方案

### 5.1 核心代码结构

```python
# skills/zhihu/zhihu_publisher.py

from playwright.sync_api import sync_playwright
import json
from typing import Optional, Dict, List

class ZhihuPublisher:
    """知乎发布器 - 基于 Playwright CDP 连接"""
    
    def __init__(self, cdp_endpoint: str = "http://localhost:9222"):
        self.cdp_endpoint = cdp_endpoint
        self.browser = None
        self.context = None
        self.page = None
        self.cdp_session = None
    
    def connect(self):
        """连接到已运行的 Chrome"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.connect_over_cdp(self.cdp_endpoint)
        
        contexts = self.browser.contexts
        self.context = contexts[0] if contexts else self.browser.new_context()
        
        pages = self.context.pages
        self.page = pages[0] if pages else self.context.new_page()
        
        # 创建 CDP Session 用于底层控制
        self.cdp_session = self.context.new_cdp_session(self.page)
        self.cdp_session.send("Network.enable")
    
    def load_cookies(self, cookie_file: str):
        """加载保存的 Cookie"""
        with open(cookie_file, 'r') as f:
            cookies = json.load(f)
        self.context.add_cookies(cookies)
    
    def save_cookies(self, cookie_file: str):
        """保存当前 Cookie"""
        cookies = self.context.cookies()
        with open(cookie_file, 'w') as f:
            json.dump(cookies, f)
    
    def publish_article(self, title: str, content: str, 
                        images: List[str] = None, topic_id: str = None) -> Dict:
        """发布知乎文章"""
        
        self.page.goto("https://zhuanlan.zhihu.com/write")
        self.page.wait_for_selector('.ProseMirror', timeout=10000)
        
        # 填写标题
        title_input = self.page.locator('input[placeholder*="标题"]')
        title_input.fill(title)
        
        # 填写内容
        editor = self.page.locator('.ProseMirror')
        editor.click()
        
        # 使用 CDP 执行输入
        self.cdp_session.send("Runtime.evaluate", {
            "expression": f'''
                const editor = document.querySelector('.ProseMirror');
                if (editor) {{
                    editor.focus();
                    document.execCommand('insertText', false, `{content}`);
                }}
            '''
        })
        
        # 上传图片
        if images:
            for img_path in images:
                self._upload_image(img_path)
        
        # 点击发布
        publish_btn = self.page.locator('button:has-text("发布")')
        publish_btn.click()
        
        self.page.wait_for_url("**/p/**", timeout=30000)
        
        return {
            "success": True,
            "url": self.page.url,
            "article_id": self.page.url.split("/p/")[-1]
        }
    
    def publish_answer(self, question_id: str, content: str) -> Dict:
        """回答问题"""
        url = f"https://www.zhihu.com/question/{question_id}/answer"
        self.page.goto(url)
        self.page.wait_for_selector('.ProseMirror', timeout=10000)
        
        editor = self.page.locator('.ProseMirror')
        editor.click()
        editor.type(content)
        
        self.page.locator('button:has-text("发布回答")').click()
        
        return {"success": True, "question_id": question_id}
    
    def _upload_image(self, image_path: str):
        """上传图片"""
        pass
    
    def close(self):
        """关闭连接"""
        if self.page:
            self.page.close()
```

### 5.2 Skill 配置

```yaml
# skills/zhihu/skill.yaml

name: zhihu-publisher
version: 1.0.0
description: 知乎内容发布 - 基于 Playwright CDP 协议

instructions: |
  你有一个知乎内容发布工具，基于 Playwright 和 Chrome DevTools Protocol 实现。
  
  主要功能：
  - 发布文章到知乎专栏
  - 回答知乎问题
  - 上传图片
  - Cookie 管理
  
  使用前提：
  1. 启动 Chrome 并开启远程调试：chrome --remote-debugging-port=9222
  2. 在浏览器中手动登录知乎（首次）
  3. Cookie 会自动保存，后续无需重复登录

tools:
  - name: zhihu:publish-article
    description: 发布文章到知乎专栏
    args:
      - title: 文章标题
      - content: 文章内容（支持 Markdown）
      - images: 图片路径列表（可选）
      - topic_id: 话题 ID（可选）
  
  - name: zhihu:publish-answer
    description: 回答知乎问题
    args:
      - question_id: 问题 ID
      - content: 回答内容
  
  - name: zhihu:upload-image
    description: 上传图片到知乎
    args:
      - image_path: 图片本地路径
  
  - name: zhihu:save-cookies
    description: 保存当前登录状态
  
  - name: zhihu:load-cookies
    description: 加载已保存的登录状态

env:
  - ZHIHU_CDP_ENDPOINT: CDP 端点地址（默认 http://localhost:9222）
  - ZHIHU_COOKIE_FILE: Cookie 存储路径（默认 ./zhihu_cookies.json）
```

### 5.3 使用流程

```bash
# 1. 启动 Chrome 并开启 CDP
chrome --remote-debugging-port=9222 --user-data-dir=/tmp/zhihu-profile

# 2. 在浏览器中手动登录知乎（首次）
```

```python
# 3. 使用发布功能
from skills.zhihu import ZhihuPublisher

publisher = ZhihuPublisher()
publisher.connect()

# 保存登录状态（首次）
publisher.save_cookies("zhihu_cookies.json")

# 发布文章
result = publisher.publish_article(
    title="AI 技术发展趋势",
    content="# 引言\n\n这是文章内容...",
    images=["./image1.png"]
)

print(f"发布成功：{result['url']}")
```

---

## 六、参考项目

### 6.1 推荐参考

| 项目 | 地址 | 说明 |
|------|------|------|
| zhihu_mcp_server | https://github.com/chemany/zhihu_mcp_server | 2025年最新，专门用于知乎发布 |
| MediaCrawler | https://github.com/NanmiCoder/MediaCrawler | 完整的知乎 API 客户端，含签名算法 |
| zhihu-plus-plus | https://github.com/zly2006/zhihu-plus-plus | Kotlin 客户端，支持 zse96 v2 签名 |

### 6.2 签名算法参考

知乎 API 需要处理 x-zse-96 签名，参考实现：
- MediaCrawler: `media_platform/zhihu/help.py`
- 签名 JS 文件: `libs/zhihu.js`

```python
# 签名流程
def sign(url: str, cookies: str) -> Dict:
    """zhihu sign algorithm"""
    import execjs
    with open("libs/zhihu.js", mode="r", encoding="utf-8-sig") as f:
        js_code = execjs.compile(f.read())
    return js_code.call("get_sign", url, cookies)
```

---

## 七、风险与防范

### 7.1 主要风险

| 风险 | 说明 |
|------|------|
| 账号封禁 | 频繁自动操作可能触发风控 |
| 验证码 | 知乎有多种验证码（倒立文字、滑块） |
| Cookie 过期 | 需要定期刷新登录状态 |
| API 变化 | 知乎可能随时更新前端代码 |

### 7.2 防范策略

1. **频率控制**：
   - 单账号日更 ≤ 3 篇
   - 发布间隔 30秒~5分钟（随机）

2. **行为模拟**：
   ```python
   import random
   import time
   
   def human_like_delay():
       delay = random.uniform(1, 3)
       time.sleep(delay)
   ```

3. **IP 隔离**（多账号场景）：
   - 每个账号使用独立代理
   - 推荐静态住宅 IP

4. **内容差异化**：
   - 避免重复内容
   - 使用 AI 改写

---

## 八、开发计划

### Phase 1: 基础功能 (1周)

- [ ] 创建 `skills/zhihu/` 目录结构
- [ ] 实现 `ZhihuPublisher` 类
- [ ] Cookie 持久化
- [ ] 文章发布功能
- [ ] 基础错误处理

### Phase 2: 完善功能 (1周)

- [ ] 图片上传
- [ ] 回答发布
- [ ] 想法发布
- [ ] 话题选择

### Phase 3: 稳定性优化 (可选)

- [ ] 验证码处理
- [ ] 登录态检测和自动刷新
- [ ] 重试机制
- [ ] 日志记录

---

## 九、文件结构

```
power-media/
├── skills/
│   └── zhihu/
│       ├── skill.yaml          # Skill 配置
│       ├── zhihu_publisher.py  # 核心实现
│       ├── zhihu_api.py        # API 封装（可选）
│       └── libs/
│           └── zhihu.js        # 签名算法（可选）
└── .sisyphus/
    └── sessions/
        └── session-zhihu-plan.md  # 本文档
```

---

## 十、变更日志

| 日期 | 变更内容 |
|------|----------|
| 2026-03-26 | 创建文档，确定技术方案 |

---

## 十一、参考资料

- [Chrome DevTools Protocol 官方文档](https://chromedevtools.github.io/devtools-protocol/)
- [Playwright CDPSession API](https://playwright.dev/docs/api/class-cdpsession)
- [Browser-Use: 从 Playwright 转向原生 CDP](https://browser-use.com/posts/playwright-to-cdp)
- [知乎 API v4 分析](https://cloud.baidu.com/article/3674679)
