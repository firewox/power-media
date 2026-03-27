---
name: get-feed
description: |
  获取小红书帖子详情。

  当用户说以下任何内容时触发此 skill：
  - "获取小红书帖子详情"
  - "查看小红书笔记内容"
  - "获取帖子内容"
  - "查看笔记详情"
  - 任何涉及获取小红书帖子详情的请求

  此 skill 自动完成：
  - 访问帖子详情页
  - 提取笔记内容、图片、评论等
  - 返回完整帖子信息

compatibility: |
  - Node.js 环境
  - Playwright
  - 依赖：playwright
---

# 获取小红书帖子详情

## 工作流程

1. 访问帖子详情页
2. 等待页面加载
3. 提取笔记内容
4. 返回完整信息

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| noteId | string | 是 | 笔记 ID 或 URL |
| loadComments | boolean | 否 | 是否加载评论，默认 false |

## 输出结果

```json
{
  "success": true,
  "noteId": "笔记ID",
  "title": "笔记标题",
  "content": "笔记正文",
  "author": {
    "userId": "作者ID",
    "username": "作者昵称"
  },
  "images": ["图片URL"],
  "likes": 100,
  "comments": []
}
```

## 使用示例

```
用户：获取小红书帖子 xxxxxx 的详情
结果：返回帖子完整信息

用户：查看这篇小红书笔记 https://www.xiaohongshu.com/explore/xxxxxx
结果：返回笔记内容
```

## 注意事项

1. 需要笔记 ID 或完整 URL
2. 部分内容可能需要登录才能查看
