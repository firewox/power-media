# publish-video

发布小红书视频笔记。

## 功能

- 上传视频文件
- 支持自定义封面
- 填写标题和正文
- 添加话题标签

## 安装依赖

```bash
cd rednote/publish-video/scripts
npm install playwright
```

## 配置

设置环境变量（可选）：

```bash
export XHS_DATA_PATH="/path/to/data"
```

## 使用方法

### 作为模块使用

```javascript
const { publishVideo } = require('./scripts/publish-video');

const result = await publishVideo({
  title: '日常vlog',
  content: '记录美好的一天...',
  video: '/path/to/video.mp4',
  cover: '/path/to/cover.jpg', // 可选
  tags: ['vlog', '日常'],
});

console.log(result);
```

### CLI 使用

```bash
node scripts/publish-video.js --title "标题" --content "内容" --video "/path/video.mp4" [--cover "/path/cover.jpg"]
```

## 输出

```json
{
  "success": true,
  "noteId": "笔记ID",
  "message": "视频笔记发布成功"
}
```

## 相关 Skills

- `check-login` - 检查登录状态
- `get-qrcode` - 获取登录二维码
- `publish-note` - 发布图文笔记
