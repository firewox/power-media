---
name: reply
description: |
  回复小红书笔记评论。

  当用户说以下任何内容时触发此 skill：
  - "回复小红书评论"
  - "回复评论"
  - "回复这条评论"
  - 任何涉及回复小红书评论的请求

  此 skill 自动完成：
  - 访问笔记页面
  - 定位目标评论
  - 填写回复内容
  - 提交回复

compatibility: |
  - Node.js 环境
  - Playwright
  - 依赖：playwright
---

# 回复小红书笔记评论

## 工作流程

1. 访问笔记详情页
2. 定位目标评论
3. 点击回复按钮
4. 填写回复内容
5. 提交回复

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| noteId | string | 是 | 笔记 ID 或 URL |
| commentId | string | 否 | 要回复的评论 ID |
| content | string | 是 | 回复内容 |

## 输出结果

```json
{
  "success": true,
  "message": "回复发表成功"
}
```

## 使用示例

```
用户：回复 xxxxxx 笔记下的评论说"谢谢支持"
结果：回复发表成功

用户：在小红书笔记 xxxxxx 回复评论 yyyyyy "同意"
结果：回复发表成功
```

## 注意事项

1. 需要登录状态
2. 如果不提供 commentId，则回复楼主评论
