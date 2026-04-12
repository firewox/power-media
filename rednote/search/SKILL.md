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
  1. 聚焦/打开创作者平台
  2. 导航到搜索页面
  3. 输入搜索关键词
  4. 截图识别搜索结果
  5. AI 提取搜索结果列表

  使用前需确保已通过 rednote-get-qrcode 完成登录。

compatibility: |
  - computer-mcp >= 1.0
  - Windows 10/11
  - Edge / Chrome 浏览器
  - Python 3.8+
---

# 搜索小红书内容

## 工作流程

### Step 1: 聚焦创作者平台

调用 `rednote_automation.find_or_open_creator()`。

### Step 2: 导航到搜索页面

```python
search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"
automation.navigate_to(search_url)
```

### Step 3: 等待加载并截图

```json
{"tool": "computer-mcp/inspect_screen", "params": {}}
```

### Step 4: AI 提取搜索结果

AI 分析截图，提取：
- 笔记标题
- 作者昵称
- 点赞数
- 笔记链接

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

1. 需要登录状态
2. 搜索结果最多返回 50 条
3. 部分内容可能需要登录才能查看
