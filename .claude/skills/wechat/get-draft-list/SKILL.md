---
name: get-draft-list
description: |
  获取微信公众号草稿箱文章列表。

  当用户说以下任何内容时触发此 skill：
  - "获取微信草稿列表"
  - "查看草稿箱"
  - "列出微信草稿"
  - "显示草稿箱内容"
  - "获取公众号草稿列表"
  - 任何涉及获取微信公众号草稿箱文章列表的请求

  此 skill 自动完成：
  - 调用微信 API 获取草稿列表
  - 返回文章列表（media_id, title, update_time 等）

  使用前必须配置微信公众号凭据。

compatibility: |
  - Node.js 环境
  - 微信公众号 AppID 和 AppSecret
  - 依赖：axios
---

# 获取微信公众号草稿箱文章列表

## 工作流程

1. 检查微信配置
2. 获取 access_token
3. 调用微信 API 获取草稿列表
4. 返回格式化的草稿列表

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| offset | number | 否 | 从全部素材的该偏移位置开始返回，默认 0 |
| count | number | 否 | 返回素材的数量，默认 20，最大 20 |

## 输出结果

```json
{
  "success": true,
  "total_count": 100,
  "item_count": 20,
  "items": [
    {
      "media_id": "xxxxxx",
      "content": {
        "news_item": [
          {
            "title": "文章标题",
            "author": "作者",
            "digest": "摘要",
            "content": "内容...",
            "thumb_media_id": "xxxxx",
            "show_cover_pic": 1,
            "url": "文章URL",
            "content_source_url": "原文链接"
          }
        ],
        "create_time": 1234567890,
        "update_time": 1234567890
      }
    }
  ]
}
```

## 配置要求

必须设置环境变量：

```bash
export WECHAT_APP_ID="你的微信公众号 AppID"
export WECHAT_APP_SECRET="你的微信公众号 AppSecret"
```

## 使用示例

**示例 1：**
```
用户：获取微信草稿列表
结果：共 50 篇草稿，返回前 20 篇...
```

**示例 2：**
```
用户：列出微信草稿，从第 20 篇开始
结果：返回第 20-39 篇草稿...
```

## 注意事项

1. **分页限制**：每次最多返回 20 条记录
2. **Token 缓存**：access_token 自动缓存
3. **时间格式**：返回的时间戳为 Unix 时间戳

## 依赖安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/.claude/skills/wechat/get-draft-list/scripts
npm install axios
```
