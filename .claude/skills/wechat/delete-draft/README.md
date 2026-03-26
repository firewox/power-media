# delete-draft

删除微信公众号草稿箱文章。

## 功能

- 根据 media_id 删除单篇草稿
- 支持 CLI 和模块调用

## 安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/.claude/skills/wechat/delete-draft/scripts
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
const { deleteDraft } = require('./scripts/delete-draft');

const result = await deleteDraft('media_id_xxxx');
console.log(result.message);
```

### CLI 使用

```bash
node scripts/delete-draft.js <mediaId>
```

示例：

```bash
node scripts/delete-draft.js xxxxxxxxxx
```

## API

### deleteDraft(mediaId)

删除草稿。

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| mediaId | string | 是 | 要删除的草稿 media_id |

**返回值：**

```javascript
{
  success: true,
  message: '草稿删除成功',
  media_id: 'xxx'
}
```
