# Upload Image to WeChat Skill

上传图片到微信公众号素材库。

## 功能特点

- ✅ 支持网络图片 URL 上传
- ✅ 支持本地图片文件上传
- ✅ 永久素材上传（无过期）
- ✅ 临时素材上传（3天有效）
- ✅ 自动重试机制（网络图片下载失败时重试3次）
- ✅ Token 自动缓存（提前5分钟刷新）

## 安装依赖

```bash
cd /mnt/d/08_tmp/02_media/power-media/.claude/skills/upload-image/scripts
bash install-deps.sh
```

或手动安装：

```bash
npm install axios form-data
```

## 配置环境变量

```bash
export WECHAT_APP_ID="你的微信公众号 AppID"
export WECHAT_APP_SECRET="你的微信公众号 AppSecret"
```

或在项目根目录创建 `.env` 文件。

## 使用方法

### 方式 1：通过 Claude 调用

```
"上传图片 https://example.com/image.jpg 到微信公众号"
"把 ./images/photo.png 上传到微信素材库"
"上传临时图片 https://example.com/tmp.gif"
```

### 方式 2：直接使用脚本

```bash
# 上传永久素材（默认）
node scripts/upload-image.js <image-url-or-path>

# 上传临时素材
node scripts/upload-image.js <image-url-or-path> --temporary
```

## 输出结果

```json
{
  "success": true,
  "media_id": "xxxxxx",
  "url": "https://mmbiz.qpic.cn/xxxx",
  "type": "image",
  "created_at": 1234567890
}
```

## 图片要求

- **格式**：JPG, PNG, GIF, BMP, WEBP
- **大小**：不超过 2MB
- **永久素材**：用于图文消息，无过期时间
- **临时素材**：用于消息接口，3天后过期

## 文件结构

```
upload-image/
├── SKILL.md              # Skill 定义
├── README.md             # 说明文档
└── scripts/
    ├── upload-image.js   # 上传脚本
    └── install-deps.sh   # 依赖安装脚本
```

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 40001 | access_token 过期，会自动重新获取 |
| 40007 | 图片格式不正确 |
| 41005 | 图片数据为空或损坏 |
| 45009 | 超过每日上传限制 |
| 48001 | API 未授权 |

## 技术实现

基于微信公众号素材管理 API：
- 永久素材：`POST /cgi-bin/material/add_material`
- 临时素材：`POST /cgi-bin/media/upload`

## TODO

- [ ] 支持批量上传
- [ ] 支持图片压缩（超过2MB时自动压缩）
