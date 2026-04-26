# push-draft-text

推送文本/Markdown 内容到微信公众号草稿箱。

## 功能

- 接收文本或 Markdown 内容
- 转换为微信兼容的 HTML 格式
- 自动处理并上传图片到素材库
- 创建微信公众号草稿

## 安装

```powershell
powershell -ExecutionPolicy Bypass -File D:\08_tmp\02_media\power-media\.claude\skills\wechat\install-deps.ps1
```

## 配置

支持以下优先级：

1. `.claude/skills/wechat/wechat-config.json`
2. 项目根目录 `.env`
3. 环境变量

环境变量示例：

```powershell
$env:WECHAT_APP_ID="你的 AppID"
$env:WECHAT_APP_SECRET="你的 AppSecret"
$env:WECHAT_DEFAULT_AUTHOR="作者名（可选）"
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

```powershell
node scripts/push-draft-text.js "<content>" "<title>" [digest] [sourceUrl] [isMarkdown]
node scripts/push-draft-text.js "<content>" "<title>" [digest] [sourceUrl] [isMarkdown] --json
```

示例：

```powershell
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
  image_count: 2,     // 处理的图片数量
  warnings: []        // 非阻断警告
}
```
