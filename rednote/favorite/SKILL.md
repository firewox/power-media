---
name: favorite
description: |
  收藏/取消收藏小红书笔记。

  当用户说以下任何内容时触发此 skill：
  - "收藏小红书笔记"
  - "取消收藏"
  - "收藏这篇笔记"
  - "小红书收藏"
  - 任何涉及小红书收藏操作的请求

  此 skill 自动完成：
  - 访问笔记页面
  - 点击收藏按钮
  - 返回操作结果

compatibility: |
  - Node.js 环境
  - Playwright
  - 依赖：playwright
---

# 收藏/取消收藏小红书笔记

## 工作流程

1. 访问笔记详情页
2. 点击收藏按钮
3. 返回操作结果

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| noteId | string | 是 | 笔记 ID 或 URL |
| unfavorite | boolean | 否 | 是否取消收藏，默认 false |

## 输出结果

```json
{
  "success": true,
  "favorited": true,
  "message": "收藏成功"
}
```

## 使用示例

```
用户：收藏这篇小红书笔记 xxxxxx
结果：收藏成功

用户：取消收藏 xxxxxx
结果：取消收藏成功
```

## 注意事项

1. 需要登录状态
2. 重复收藏会自动取消
