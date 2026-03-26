# get-draft-detail

获取微信公众号草稿箱文章详情。

## 功能

- 根据 media_id 获取草稿详情
- 返回文章的完整信息（标题、作者、内容等）
- 返回 HTML 格式的文章内容

## 安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/.claude/skills/wechat/get-draft-detail/scripts
chmod +x install-deps.sh
./install-deps.sh
```

或手动安装：

```bash
npm install axios
```

## 配置

设置环境变量：

```bash
export WECHAT_APP_ID="你的 AppID"
export WECHAT_APP_SECRET="你的 AppSecret"
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

```bash
node scripts/get-draft-detail.js <mediaId>
```

示例：

```bash
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
