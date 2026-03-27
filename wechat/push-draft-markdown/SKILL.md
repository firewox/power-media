---
name: push-draft-file
description: |
  从 Markdown 文件推送文章到微信公众号草稿箱。

  当用户说以下任何内容时触发此 skill：
  - "推送 Markdown 文件到微信草稿箱"
  - "把 md 文件发布到微信草稿"
  - "从文件创建微信文章"
  - "上传 Markdown 到微信公众号"
  - "发布文章到微信草稿"
  - 任何涉及从文件推送文章到微信公众号草稿箱的请求

  此 skill 自动完成：
  - 读取 Markdown 文件
  - 转换 Markdown 为微信兼容 HTML
  - 上传图片到素材库
  - 生成封面图（如无图片）
  - 创建微信草稿

  使用前必须配置微信公众号凭据。

compatibility: |
  - Node.js 环境
  - 微信公众号 AppID 和 AppSecret
  - 依赖：axios, form-data, marked, sanitize-html, highlight.js, sharp
---

# 从文件推送文章到微信公众号草稿箱

## 工作流程

1. 检查微信配置
2. 读取 Markdown 文件内容
3. 处理 Markdown：
   - 提取并上传图片到素材库
   - 转换 Markdown 为 HTML
   - 应用微信兼容样式
4. 生成或选择封面图：
   - 优先使用文章中的第一张图片
   - 或查找本地 thumbnail 文件
   - 或自动生成 SVG 封面图
5. 调用微信 API 创建草稿
6. 返回 media_id 和结果信息

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| filePath | string | 是 | Markdown 文件绝对路径 |
| title | string | 是 | 文章标题 |
| digest | string | 否 | 文章摘要（如未提供自动提取）|
| sourceUrl | string | 否 | 原文链接 |

## 输出结果

```json
{
  "success": true,
  "media_id": "xxxxxx",
  "message": "文章成功添加到草稿箱",
  "imageCount": 3,
  "firstImageMediaId": "xxxxx"
}
```

## 配置要求

必须设置环境变量：

```bash
export WECHAT_APP_ID="你的微信公众号 AppID"
export WECHAT_APP_SECRET="你的微信公众号 AppSecret"
export WECHAT_DEFAULT_AUTHOR="作者名（可选）"
export WECHAT_NEED_OPEN_COMMENT="true（可选）"
export WECHAT_ONLY_FANS_CAN_COMMENT="true（可选）"
```

## 封面图优先级

1. 文章中的第一张图片（自动上传为素材）
2. 本地文件：
   - ./thumbnail.png
   - ./thumbnail.jpg
   - ./default-cover.png
3. 自动生成 SVG 渐变封面图

## 使用示例

**示例 1：**
```
用户：推送 /home/user/article.md 到微信草稿，标题是"AI发展趋势"
结果：media_id: xxxxx, 已处理图片: 2张
```

**示例 2：**
```
用户：把 ./posts/blog.md 发布到微信公众号草稿
结果：media_id: xxxxx, 自动生成封面图
```

## 注意事项

1. **图片处理**：自动提取并上传 Markdown 中的图片
2. **路径解析**：支持绝对路径和相对路径
3. **自动重试**：网络图片下载失败时自动重试 3 次
4. **Token 缓存**：access_token 自动缓存

## 依赖安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/.claude/skills/wechat/push-draft-file/scripts
npm install axios form-data marked sanitize-html highlight.js sharp
```
