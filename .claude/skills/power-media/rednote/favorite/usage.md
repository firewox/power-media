# favorite

收藏/取消收藏小红书笔记。

## 安装依赖

```bash
cd rednote/favorite/scripts
npm install playwright
```

## 使用方法

```javascript
const { favorite } = require('./scripts/favorite');

const result = await favorite({ noteId: 'xxxxxx' });
console.log(result);
```

### CLI

```bash
node scripts/favorite.js --noteId "笔记ID" [--unfavorite]
```

## 相关 Skills

- `like` - 点赞笔记
- `comment` - 发表评论
