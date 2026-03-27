# like

点赞/取消点赞小红书笔记。

## 安装依赖

```bash
cd rednote/like/scripts
npm install playwright
```

## 使用方法

```javascript
const { like } = require('./scripts/like');

const result = await like({ noteId: 'xxxxxx' });
console.log(result);
```

### CLI

```bash
node scripts/like.js --noteId "笔记ID" [--unlike]
```

## 相关 Skills

- `favorite` - 收藏笔记
- `comment` - 发表评论
