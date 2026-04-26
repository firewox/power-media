# reply

回复小红书笔记评论。

## 安装依赖

```bash
cd rednote/reply/scripts
npm install playwright
```

## 使用方法

```javascript
const { reply } = require('./scripts/reply');

const result = await reply({
  noteId: 'xxxxxx',
  commentId: 'yyyyyy',
  content: '谢谢支持！'
});
console.log(result);
```

### CLI

```bash
node scripts/reply.js --noteId "笔记ID" [--commentId "评论ID"] --content "回复内容"
```

## 相关 Skills

- `comment` - 发表评论
- `get-feed` - 获取帖子详情
