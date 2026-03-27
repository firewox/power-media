---
name: get-profile
description: |
  获取小红书用户主页信息。

  当用户说以下任何内容时触发此 skill：
  - "获取小红书用户主页"
  - "查看小红书用户信息"
  - "小红书用户资料"
  - "获取用户主页"
  - 任何涉及获取小红书用户主页的请求

  此 skill 自动完成：
  - 访问用户主页
  - 提取用户信息
  - 获取用户笔记列表

compatibility: |
  - Node.js 环境
  - Playwright
  - 依赖：playwright
---

# 获取小红书用户主页

## 工作流程

1. 访问用户主页
2. 等待页面加载
3. 提取用户信息
4. 获取笔记列表

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| userId | string | 是 | 用户 ID 或主页 URL |

## 输出结果

```json
{
  "success": true,
  "userId": "用户ID",
  "username": "用户昵称",
  "desc": "用户简介",
  "fans": 1000,
  "following": 100,
  "notes": []
}
```

## 使用示例

```
用户：获取小红书用户 xxxxxx 的主页信息
结果：返回用户信息和笔记列表

用户：查看这个用户的主页 https://www.xiaohongshu.com/user/profile/xxxxxx
结果：返回用户资料
```

## 注意事项

1. 需要用户 ID 或完整 URL
2. 部分信息可能需要登录才能查看
