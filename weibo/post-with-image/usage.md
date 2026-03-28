# post-with-image

使用浏览器自动化发布带图片的微博。

## 功能

- 自动检查登录状态
- 上传本地图片
- 发布带图片的微博
- 支持 140 字符限制

## 安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/weibo/post-with-image/scripts
npm install playwright
npx playwright install chromium
```

## 使用方法

### CLI 使用

```bash
node scripts/post-with-image.js "微博内容" "/path/to/image.jpg"
```

示例：

```bash
node scripts/post-with-image.js "分享美景" "./photo.jpg"
```

### 输出示例

**成功：**
```
正在检查登录状态...
已登录

正在发布带图片的微博...
图片: ./photo.jpg
发布成功！
```

**失败（图片不存在）：**
```
错误: 图片文件不存在: ./photo.jpg
```

## 工作流程

1. **检查登录**
   - 验证 Cookie 是否有效
   - 未登录则提示先登录

2. **验证图片**
   - 检查文件是否存在
   - 检查文件格式

3. **启动浏览器**
   - 使用 headless 模式
   - 加载保存的 Cookie

4. **打开发布页面**
   - 访问微博首页
   - 等待页面加载

5. **填写内容**
   - 找到文本输入框
   - 填入微博内容

6. **上传图片**
   - 找到图片上传控件
   - 选择本地图片文件
   - 等待图片上传完成

7. **点击发送**
   - 找到发送按钮
   - 点击发布

8. **检查结果**
   - 检查成功/失败提示
   - 返回结果

## 前置条件

必须先运行 login skill 登录：

```bash
node ../login/scripts/login.js
```

## 图片要求

- 格式：JPG, PNG, GIF
- 大小：建议不超过 5MB
- 路径：绝对路径或相对路径

## 限制

- 微博内容最多 140 字符
- 单次只能上传一张图片（多图需多次调用）
- 需要有效的登录 Cookie
