# push-draft-text

推送文本/Markdown 内容到微信公众号草稿箱。

## 功能

- 接收文本或 Markdown 内容
- 转换为微信兼容的 HTML 格式
- 自动处理并上传图片到素材库
- 创建微信公众号草稿

## 安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/.claude/skills/wechat/push-draft-text/scripts
chmod +x install-deps.sh
./install-deps.sh
```

或手动安装：

```bash
npm install axios form-data marked sanitize-html highlight.js sharp
```

## 配置

设置环境变量：

```bash
export WECHAT_APP_ID="你的 AppID"
export WECHAT_APP_SECRET="你的 AppSecret"
export WECHAT_DEFAULT_AUTHOR="作者名（可选）"
```

## 使用方法

### 作为模块使用

```javascript
const { pushDraftText } = require('./scripts/push-draft-text');

const result = await pushDraftText({
  content: '# 标题\n\n正文内容...',
  title: '文章标题',
  digest: '摘要（可选）',
  sourceUrl: 'https://example.com（可选）',
  isMarkdown: true
});

console.log(result.media_id);
```

### CLI 使用

```bash
node scripts/push-draft-text.js "<content>" "<title>" [digest] [sourceUrl] [isMarkdown]
```

示例：

```bash
node scripts/push-draft-text.js "# 技术分享" "技术文章标题" "文章摘要" "" true
```

## API

### pushDraftText(options)

推送内容到微信草稿箱。

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| options.content | string | 是 | 文章内容 |
| options.title | string | 是 | 文章标题 |
| options.digest | string | 否 | 文章摘要 |
| options.sourceUrl | string | 否 | 原文链接 |
| options.isMarkdown | boolean | 否 | 是否为 Markdown，默认 true |

**返回值：**

```javascript
{
  success: true,      // 是否成功
  media_id: 'xxx',    // 草稿 media_id
  message: '...',     // 结果消息
  imageCount: 2       // 处理的图片数量
}
```
