# post-with-image

发布带图片的微博到新浪微博。

## 功能

- 验证微博内容长度（140 字符限制）
- 验证图片格式和大小（最大 5MB）
- 发布带图片的微博
- 返回发布结果和微博链接

## 安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/weibo/post-with-image/scripts
pip3 install requests python-dotenv
```

## 配置

设置环境变量：

```bash
export WEIBO_ACCESS_TOKEN="你的 Access Token"
```

## 使用方法

### CLI 使用

```bash
python3 scripts/post-with-image.py "微博内容" "/path/to/image.jpg"
```

示例：

```bash
python3 scripts/post-with-image.py "分享一张美景" "./photo.jpg"
```

### 作为模块使用

```python
from scripts.post_with_image import WeiboPoster

poster = WeiboPoster(access_token)
result = poster.post_with_image("微博内容", "/path/to/image.jpg")
print(result)
```

## 图片要求

- 格式: JPEG, GIF, PNG
- 大小: 单张最大 5MB
- 路径: 绝对路径或相对路径

## 输出格式

```json
{
  "success": true,
  "weibo_id": "1234567890",
  "url": "https://weibo.com/xxx/xxx",
  "created_at": "Mon Mar 27 10:30:00 +0800 2026",
  "text": "微博内容",
  "pic_url": "http://wx.sinaimg.cn/xxx.jpg"
}
```

## 注意事项

- 图片文件必须存在且可读
- 单张图片最大 5MB
- 支持的格式：JPEG, GIF, PNG
