---
name: get-draft-detail
description: |
  获取微信公众号草稿箱文章详情。

  当用户说以下任何内容时触发此 skill：
  - "获取微信草稿详情"
  - "查看草稿内容"
  - "获取文章详情"
  - "显示草稿详情"
  - "查看微信草稿内容"
  - 任何涉及获取微信公众号草稿箱文章详情的请求

  此 skill 自动完成：
  - 根据 media_id 获取草稿详情
  - 返回文章内容、标题、作者等完整信息

  使用前必须配置微信公众号凭据。

compatibility: |
  - Node.js 环境
  - 微信公众号 AppID 和 AppSecret
  - 依赖：axios
---

# 获取微信公众号草稿箱文章详情

## 工作流程

1. 检查微信配置
2. 获取 access_token
3. 调用微信 API 获取草稿详情
4. 返回完整的草稿内容

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| mediaId | string | 是 | 草稿的 media_id |

## 输出结果

```json
{
  "success": true,
  "media_id": "xxxxxx",
  "title": "文章标题",
  "author": "作者",
  "digest": "摘要",
  "content": "HTML内容...",
  "thumb_media_id": "封面图media_id",
  "show_cover_pic": 1,
  "url": "文章URL",
  "content_source_url": "原文链接",
  "need_open_comment": 0,
  "only_fans_can_comment": 0,
  "create_time": 1234567890,
  "update_time": 1234567890
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
用户：获取草稿详情，media_id 是 xxxxx
结果：返回该草稿的完整内容...
```

**示例 2：**
```
用户：查看微信草稿 xxxxx 的内容
结果：显示文章标题、作者、正文等信息...
```

## 注意事项

1. **media_id 获取**：可通过 get-draft-list 获取草稿列表
2. **内容格式**：返回的 content 为 HTML 格式
3. **Token 缓存**：access_token 自动缓存

## 依赖安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/.claude/skills/wechat/get-draft-detail/scripts
npm install axios
```
