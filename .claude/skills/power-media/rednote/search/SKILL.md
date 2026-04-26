---
name: rednote-search
description: |
  搜索小红书内容。

  当用户说以下任何内容时触发此 skill：
  - "搜索小红书"
  - "在小红书搜索"
  - "小红书搜索内容"
  - "查找小红书笔记"
  - 任何涉及搜索小红书内容的请求

  工作流程：
  1. 聚焦/打开小红书浏览页面 (explore)
  2. 导航到搜索结果 URL
  3. 截图，多模态 AI 直接分析提取搜索结果

  使用前需确保已通过 rednote-get-qrcode 完成登录。

compatibility: |
  - computer-mcp >= 1.0
  - Windows 10/11
  - Edge / Chrome 浏览器
  - Python 3.8+
---

# 搜索小红书内容

## 关键规则 ⚠️

### 1. 平台区分（强制遵守）

| 平台 | URL | 用途 | 禁止操作 |
|------|-----|------|---------|
| **创作服务平台** | `creator.xiaohongshu.com` | 发布笔记、笔记管理、数据看板 | 搜索、查看他人内容 |
| **用户浏览页面** | `www.xiaohongshu.com/explore` | 搜索笔记、查看笔记、浏览他人内容 | 发布笔记 |

**搜索操作必须在用户浏览页面进行，不是在创作平台。**

### 2. 禁止硬编码坐标点击浏览器 UI

- ❌ **不要**通过固定坐标 (如 `(0.5, 0.13)`) 点击浏览器的标签页、地址栏、搜索框
- ❌ **不要**尝试模拟点击浏览器 chrome 区域（Y < 10% 的窗口区域）
- ✅ **使用 URL 直接导航** 到搜索结果页面
- ✅ **使用多模态 AI 分析截图** 识别页面内元素坐标

## 工作流程

### Step 1: 聚焦浏览页面

调用 `rednote_automation.find_or_open_creator(page_type="explore")`。

### Step 2: 导航到搜索结果页面

```python
search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"
automation.navigate_to(search_url)
automation.mcp.wait(4)  # 等待页面加载完成
```

### Step 3: 截图验证

```python
result = automation.mcp.inspect_screen()
```

**AI 验证要点**:
- URL 是否包含 `search_result`
- 页面是否显示搜索关键词
- 是否加载了搜索结果卡片

### Step 4: 多模态 AI 提取搜索结果

多模态 AI 直接观察截图，提取：
- 笔记标题
- 作者昵称
- 点赞数
- 笔记链接
- 发布时间

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | 搜索关键词 |
| sortBy | string | 否 | 排序方式：综合/最新/最多点赞 |

## 输出结果

```json
{
  "success": true,
  "keyword": "搜索关键词",
  "screenshot_path": "D:\\...\\rednote_search_xxx.png",
  "message": "请 AI 分析截图提取搜索结果"
}
```

## 注意事项

1. **需要登录状态** - 部分内容需要登录才能查看
2. **搜索结果最多返回 50 条** - 分页需要滚动加载
3. **URL 导航优先** - 对于搜索操作，优先构造搜索 URL 跳转，而不是模拟输入
4. **页面验证** - 每次导航后截图确认 URL 和内容是否正确
5. **错误重试** - 如果导航失败，最多重试 2 次

## 常见问题

### Q: 搜索框在哪里？如何点击搜索框？

**A**: 不要点击搜索框。直接导航到搜索 URL：
```python
url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"
automation.navigate_to(url)
```

### Q: 如何确认当前页面是正确的？

**A**: AI 分析截图确认：
1. 地址栏 URL 是否包含 `search_result`
2. 页面顶部是否显示搜索关键词
3. 是否显示搜索结果卡片

### Q: 为什么坐标点击会失败？

**A**: 浏览器 chrome（标签页+地址栏+书签栏）占据窗口约 10-15% 的高度。
硬编码坐标容易误触浏览器 UI 元素，而不是页面内容。
**解决方案**: 优先使用 URL 导航，或让 AI 分析截图后给出精确坐标。
