---
name: push-draft-text
description: |
  推送文本/Markdown 内容到微信公众号草稿箱。

  当用户说以下任何内容时触发此 skill：
  - "推送文本到微信草稿"
  - "发布内容到微信公众号"
  - "创建微信草稿"
  - "推送文章到微信草稿箱"
  - "把内容发布到微信公众号"
  - 任何涉及推送文本或 Markdown 内容到微信公众号草稿箱的请求

  此 skill 自动完成：
  - 接收文本/Markdown 内容
  - 转换为微信兼容 HTML
  - 处理并上传图片到素材库
  - 创建微信草稿

  使用前必须配置微信公众号凭据。

compatibility: |
  - Node.js 环境
  - 微信公众号 AppID 和 AppSecret
  - 依赖：axios, form-data, marked, sanitize-html, highlight.js, sharp
---

# 推送文本/Markdown 到微信公众号草稿箱

## 工作流程

1. 检查微信配置
2. 接收文本/Markdown 内容
3. 处理内容：
   - 转换 Markdown 为 HTML
   - 应用微信兼容样式
   - 处理图片（提取网络图片并上传）
4. 调用微信 API 创建草稿
5. 返回 media_id 和结果信息

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | string | 是 | 文章内容（文本或 Markdown 格式）|
| title | string | 是 | 文章标题 |
| digest | string | 否 | 文章摘要（如未提供自动提取前 120 字）|
| sourceUrl | string | 否 | 原文链接 |
| isMarkdown | boolean | 否 | 内容是否为 Markdown 格式，默认 true |

## 输出结果

```json
{
  "success": true,
  "media_id": "xxxxxx",
  "message": "文章成功添加到草稿箱",
  "imageCount": 2
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

## 使用示例

**示例 1：**
```
用户：推送一篇微信草稿，标题是"AI发展趋势"，内容是"## 人工智能的发展..."
结果：media_id: xxxxx, 文章成功添加到草稿箱
```

**示例 2：**
```
用户：发布以下内容到微信公众号："# 技术分享
> 今天我们来讨论..."
结果：media_id: xxxxx, 文章成功添加到草稿箱
```

## 注意事项

1. **Markdown 支持**：支持完整的 Markdown 语法，包括标题、列表、代码块、引用等
2. **图片处理**：自动处理 Markdown 中的网络图片，上传到微信素材库
3. **代码高亮**：代码块会自动应用语法高亮
4. **Token 缓存**：access_token 自动缓存

## 依赖安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/.claude/skills/wechat/push-draft-text/scripts
npm install axios form-data marked sanitize-html highlight.js sharp
```
