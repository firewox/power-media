---
name: rednote-publish-note
description: |
  发布小红书图文笔记。

  当用户说以下任何内容时触发此 skill：
  - "发布小红书笔记"
  - "发小红书图文"
  - "发布图文到小红书"
  - "发一篇小红书"
  - 任何涉及发布小红书图文笔记的请求

  工作流程：
  1. 检查登录状态
  2. 导航到创作者中心发布页
  3. 选择"上传图文"
  4. 上传图片文件
  5. 填写标题和正文
  6. 添加话题标签
  7. 设置可见范围等选项
  8. 点击发布并确认

  使用前需确保已通过 rednote-get-qrcode 完成登录。

compatibility: |
  - computer-mcp >= 1.0
  - Windows 10/11
  - Edge / Chrome 浏览器
  - Python 3.8+
---

# 发布小红书图文笔记

## 工作流程

### Step 1: 前置检查

调用 `rednote-check-login` 确认已登录。

### Step 2: 导航到发布页

```json
{
  "tool": "computer-mcp/hotkey",
  "params": {"keys": ["ctrl", "l"]}
}
```

输入 URL: `creator.xiaohongshu.com/publish/publish`

或直接调用 `rednote_automation.navigate_to(automation.PUBLISH_URL)`

### Step 3: 选择"上传图文"

调用 `inspect_screen()` 截图，多模态 AI 直接观察页面找到"上传图文"按钮并返回坐标。

### Step 4: 上传图片

1. 调用 `inspect_screen()` 找上传区域
2. 点击上传区域触发文件选择对话框
3. 输入图片路径
4. 按回车确认
5. 等待 5 秒上传完成

### Step 5: 填写标题

1. 找到标题输入框
2. 点击聚焦
3. 输入标题内容（最多 20 字）

### Step 6: 填写正文

1. 找到正文编辑器
2. 点击聚焦
3. 输入正文内容（最多 1000 字）

### Step 7: 添加话题标签

在正文中输入 `#话题` 格式，最多 10 个标签。

### Step 8: 设置可见范围

根据参数设置可见范围：
- `public`: 公开
- `friends`: 仅好友可见
- `private`: 仅自己可见

### Step 9: 点击发布

1. 找到"发布"按钮
2. 点击发布
3. 调用 `confirm_action("确认发布小红书笔记？")`

### Step 10: 验证结果

调用 `inspect_screen()` 检查"发布成功"提示。

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 笔记标题（最多 20 字） |
| content | string | 是 | 笔记正文（最多 1000 字） |
| images | string[] | 是 | 图片路径数组（最多 18 张） |
| tags | string[] | 否 | 话题标签数组（最多 10 个） |
| visibility | string | 否 | 可见范围：public/friends/private，默认 public |

## 输出结果

**成功**:
```json
{
  "success": true,
  "message": "笔记发布成功",
  "screenshot_path": "D:\\...\\rednote_publish_result_xxx.png"
}
```

**发布页就绪**:
```json
{
  "success": true,
  "message": "已到达发布页，请 AI 分析截图并指导后续操作",
  "screenshot_path": "D:\\...\\rednote_publish_page_xxx.png",
  "params": {...},
  "next_steps": [...]
}
```

## 配置要求

环境变量：
- 无特殊要求

## 使用示例

```
用户：发布一篇小红书，标题"美食分享"，内容"今天做了..."，图片是 ["/path/1.jpg", "/path/2.jpg"]
结果：已到达发布页，请 AI 分析截图并指导后续操作

用户：发小红书图文，标题"旅行记录"，内容"..."，上传图片并添加话题 #旅行
结果：笔记发布成功
```

## 注意事项

1. 标题最多 20 个字
2. 正文最多 1000 个字
3. 图片最多 18 张，支持 JPG/PNG 格式
4. 话题标签最多 10 个
5. 每日发布量有限制（约 50 篇）
6. 发布前需确保已登录
7. 高风险操作需人工确认
