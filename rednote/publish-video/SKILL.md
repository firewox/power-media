---
name: rednote-publish-video
description: |
  发布小红书视频笔记。

  当用户说以下任何内容时触发此 skill：
  - "发布小红书视频"
  - "发视频到小红书"
  - "上传视频到小红书"
  - 任何涉及发布小红书视频笔记的请求

  工作流程：
  1. 检查登录状态
  2. 导航到创作者中心发布页
  3. 选择"上传视频"
  4. 上传视频文件
  5. 填写标题和正文
  6. 设置封面（可选）
  7. 添加话题标签
  8. 设置可见范围等选项
  9. 点击发布并确认

  使用前需确保已通过 rednote-get-qrcode 完成登录。

compatibility: |
  - computer-mcp >= 1.0
  - Windows 10/11
  - Edge / Chrome 浏览器
  - Python 3.8+
---

# 发布小红书视频笔记

## 工作流程

与 `rednote-publish-note` 类似，区别在于：

### Step 3: 选择"上传视频"

调用 `inspect_screen()` 识别"上传视频"按钮（而非"上传图文"）并点击。

### Step 4: 上传视频

1. 点击上传区域
2. 输入视频文件路径（MP4 格式）
3. 按回车确认
4. 等待上传（可能需要较长时间，取决于视频大小）

### Step 6: 设置封面（可选）

如提供封面图片：
1. 找到"设置封面"按钮
2. 上传封面图片
3. 调整封面裁剪区域

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 笔记标题（最多 20 字） |
| content | string | 否 | 笔记正文（最多 1000 字） |
| video | string | 是 | 视频文件路径（MP4 格式，≤2GB） |
| cover | string | 否 | 封面图片路径（可选） |
| tags | string[] | 否 | 话题标签数组（最多 10 个） |
| visibility | string | 否 | 可见范围：public/friends/private，默认 public |

## 输出结果

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

## 视频要求

- 格式：MP4
- 大小：建议 ≤ 2GB
- 时长：1 分钟 ~ 15 分钟

## 注意事项

1. 视频上传可能需要较长时间
2. 建议提供封面图片以提升视觉效果
3. 其他限制与图文笔记相同
