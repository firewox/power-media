# comment

在小红书笔记下发表评论。

## 安装依赖

```bash
cd rednote/comment/scripts
npm install playwright
```

## 使用方法

```javascript
const { comment } = require('./scripts/comment');

const result = await comment({
  noteId: 'xxxxxx',
  content: '写得好！'
});
console.log(result);
```

### CLI

```bash
node scripts/comment.js --noteId "笔记ID" --content "评论内容"
```

## 相关 Skills

- `like` - 点赞笔记
- `reply` - 回复评论
