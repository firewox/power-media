---
name: enhance-image
description: |
  使用 Pillow 增强扫描文档和图片清晰度，支持多种预设和模式。

  当用户说以下内容时触发此 skill：
  - "增强图片"
  - "图片增强"
  - "增强扫描件"
  - "扫描件增强"
  - "enhance image"
  - "图片清晰化"
  - "提升图片质量"
  - 任何涉及增强图片/文档清晰度的请求

  脚本执行：
  ```bash
  python enhance-image/scripts/enhance_image.py <image_path> [options]
  ```

  功能：
  - 支持多种预设（soft / document / strong）
  - 支持 color / grayscale / bw 三种输出模式
  - 可调对比度、锐度、亮度
  - 支持中值降噪
  - 支持缩放

  依赖：
  - Pillow >= 12.2.0

compatibility:
  - Python >= 3.12
  - Pillow >= 12.2.0
---

# 图片增强工具

## 脚本调用

### 直接执行脚本
```bash
# 使用 document 预设（默认）
python enhance-image/scripts/enhance_image.py scan.png

# 使用 soft 预设，输出灰度图
python enhance-image/scripts/enhance_image.py scan.png --preset soft --mode grayscale

# 使用 strong 预设，输出黑白图，2x 缩放
python enhance-image/scripts/enhance_image.py scan.png --preset strong --mode bw --scale 2.0

# 自定义参数
python enhance-image/scripts/enhance_image.py scan.png --contrast 1.5 --sharpness 2.0 --denoise

# 指定输出路径
python enhance-image/scripts/enhance_image.py scan.png --output enhanced.png
```

### 从 Python 调用
```python
from enhance_image.scripts.enhance_image import enhance_image

# 使用 document 预设
output = enhance_image("scan.png")

# 使用 strong 预设，黑白模式
output = enhance_image("scan.png", mode="bw", preset="strong")

# 自定义参数
output = enhance_image("scan.png", contrast=1.5, sharpness=2.0, denoise=True, scale=2.0)
```

## 预设说明

| 预设 | 对比度 | 锐度 | 亮度 | 降噪 | 适用场景 |
|------|--------|------|------|------|---------|
| soft | 1.12 | 1.35 | 1.0 | 否 | 轻微增强，保留原质感 |
| document | 1.22 | 1.90 | 1.02 | 否 | 扫描文档增强，推荐 |
| strong | 1.35 | 2.40 | 1.03 | 否 | 强烈增强，适合模糊图片 |

## 输出模式

| 模式 | 说明 |
|------|------|
| color | 彩色输出（默认） |
| grayscale | 灰度图 |
| bw | 黑白二值图（可调 threshold） |

## 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| image | str | - | 输入图片路径（必填） |
| --output | str | 自动 | 输出路径，默认 `<原文件名>-enhanced.png` |
| --mode | str | color | 输出模式：color/grayscale/bw |
| --preset | str | document | 预设：soft/document/strong |
| --contrast | float | 预设值 | 对比度 |
| --sharpness | float | 预设值 | 锐度 |
| --brightness | float | 预设值 | 亮度 |
| --scale | float | 1.0 | 缩放倍数 |
| --threshold | int | 185 | 黑白二值化阈值（仅 bw 模式） |
| --denoise | flag | 否 | 应用中值降噪 |

## 输出格式

支持输出扩展名：bmp, jpeg, jpg, png, tif, tiff, webp

## 注意事项

1. `--denoise` 会软化文字边缘，对文档扫描件慎用
2. `--mode bw` 结合 `--threshold` 可产生清晰的扫描件效果
3. `--scale` 使用 LANCZOS 重采样，在放大的同时保持较高画质
