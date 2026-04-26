# post-text

使用浏览器自动化发布纯文本微博。

## 功能

- 自动检查登录状态
- 发布纯文本微博
- 返回发布结果
- 支持 140 字符限制

## 安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/weibo/post-text/scripts
npm install playwright
npx playwright install chromium
```

## 使用方法

### CLI 使用

```bash
node scripts/post-text.js "微博内容"
```

示例：

```bash
node scripts/post-text.js "Hello Weibo! 👋"
```

### 输出示例

**成功：**
```
正在检查登录状态...
已登录

正在发布微博...
发布成功！
```

**失败：**
```
正在检查登录状态...
未登录
请先运行 login skill 进行登录
```

## 工作流程

1. **检查登录**
   - 验证 Cookie 是否有效
   - 未登录则提示先登录

2. **启动浏览器**
   - 使用 headless 模式
   - 加载保存的 Cookie

3. **打开发布页面**
   - 访问微博首页
   - 等待页面加载

4. **填写内容**
   - 找到文本输入框
   - 填入微博内容

5. **点击发送**
   - 找到发送按钮
   - 点击发布

6. **检查结果**
   - 检查成功/失败提示
   - 返回结果

## 前置条件

必须先运行 login skill 登录：

```bash
node ../login/scripts/login.js
```

## 限制

- 微博内容最多 140 字符
- 每小时有发布频率限制
- 需要有效的登录 Cookie
