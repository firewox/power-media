# get-draft-detail

获取微信公众号草稿箱文章详情。

## 功能

- 根据 media_id 获取草稿详情
- 返回文章的完整信息（标题、作者、内容等）
- 返回 HTML 格式的文章内容

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
```

## 使用方法

### 作为模块使用

```javascript
const { getDraftDetail } = require('./scripts/get-draft-detail');

const result = await getDraftDetail('media_id_xxxx');
console.log(result.title);
console.log(result.content);
```

### CLI 使用

```powershell
node scripts/get-draft-detail.js <mediaId>
node scripts/get-draft-detail.js <mediaId> --json
```

示例：

```powershell
node scripts/get-draft-detail.js xxxxxxxxxx
```

## API

### getDraftDetail(mediaId)

获取草稿详情。

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| mediaId | string | 是 | 草稿的 media_id |

**返回值：**

```javascript
{
  success: true,
  media_id: 'xxx',
  title: '文章标题',
  author: '作者',
  digest: '摘要',
  content: 'HTML内容...',
  thumb_media_id: '封面图media_id',
  show_cover_pic: 1,
  url: '文章URL',
  content_source_url: '原文链接',
  need_open_comment: 0,
  only_fans_can_comment: 0,
  create_time: 1234567890,
  update_time: 1234567890,
  create_time_formatted: '2024/1/1 12:00:00',
  update_time_formatted: '2024/1/1 12:00:00'
}
```
