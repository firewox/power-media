# login

使用扫码方式登录微博。

## 功能

- 打开浏览器显示微博登录页
- 自动切换到扫码登录模式
- 显示二维码供用户扫描
- 等待扫码完成
- 保存登录 Cookie

## 安装

```bash
cd /mnt/d/08_tmp/02_media/power-media/weibo/login/scripts
npm install playwright
npx playwright install chromium
```

## 使用方法

### CLI 使用

```bash
node scripts/login.js
```

### 输出示例

```
正在打开微博登录页面...

请使用微博 APP 扫描二维码登录...
[二维码显示在浏览器中]

登录成功！
用户名: 张三
Cookie 已保存
```

## 登录流程

1. **启动浏览器**
   - 打开 Chromium 浏览器
   - 访问 https://weibo.com

2. **切换扫码登录**
   - 自动点击"扫码登录"标签

3. **显示二维码**
   - 等待二维码加载
   - 二维码显示在浏览器中

4. **用户扫码**
   - 打开手机微博 APP
   - 扫描二维码
   - 在手机上确认登录

5. **保存 Cookie**
   - 登录成功后自动保存
   - 保存到 `weibo/.cookies.json`

6. **关闭浏览器**

## Cookie 文件

- 路径：`weibo/.cookies.json`
- 包含登录会话信息
- 有效期：通常几天到几周
- 过期后需要重新登录

## 常见问题

**Q: 二维码过期怎么办？**
A: 关闭脚本重新运行，会生成新的二维码。

**Q: 可以保存多个账号吗？**
A: 当前只支持单账号，Cookie 会被覆盖。
