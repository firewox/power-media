# Push Draft File Skill

从 Markdown 文件推送文章到微信公众号草稿箱。

## 功能特点

- ✅ 读取 Markdown 文件
- ✅ 自动转换 Markdown 为微信 HTML
- ✅ 自动上传图片到素材库
- ✅ 自动生成封面图（SVG 渐变）
- ✅ 支持自定义标题、摘要、原文链接
- ✅ Token 自动缓存

## 安装依赖

```bash
cd /mnt/d/08_tmp/02_media/power-media/.claude/skills/wechat/push-draft-file/scripts
npm install axios form-data marked sanitize-html highlight.js sharp
```

## 配置环境变量

```bash
export WECHAT_APP_ID="你的 AppID"
export WECHAT_APP_SECRET="你的 AppSecret"
export WECHAT_DEFAULT_AUTHOR="作者名（可选）"
export WECHAT_NEED_OPEN_COMMENT="true（可选）"
export WECHAT_ONLY_FANS_CAN_COMMENT="true（可选）"
```

## 使用方法

### 方式 1：通过 Claude 调用

```
"推送 /home/user/article.md 到微信草稿，标题是'AI发展趋势'"
"把 ./posts/blog.md 发布到微信公众号草稿"
```

### 方式 2：直接使用脚本

```bash
node scripts/push-draft-file.js <filePath> <title> [digest] [sourceUrl]
```

## 封面图优先级

1. 文章中的第一张图片
2. 本地文件：./thumbnail.png, ./thumbnail.jpg, ./default-cover.png
3. 自动生成 SVG 渐变封面图

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
