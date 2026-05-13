---
name: image-to-pdf
description: |
  使用 PyMuPDF 将单张图片转换为单页 PDF，支持 JPEG 压缩控制文件大小。

  当用户说以下内容时触发此 skill：
  - "图片转PDF"
  - "图片转成PDF"
  - "image to pdf"
  - "图片转换成PDF"
  - "扫描件转PDF"
  - "把图片变成PDF"
  - 任何涉及将图片转换为 PDF 的请求

  脚本执行：
  ```bash
  python image-to-pdf/scripts/image_to_pdf.py <image_path> [options]
  ```

  功能：
  - 单张图片转单页 PDF（原始质量）
  - JPEG 压缩控制文件大小（指定目标大小或固定品质）

  依赖：
  - PyMuPDF >= 1.26.7

compatibility:
  - Python >= 3.12
  - PyMuPDF >= 1.26.7
---

# 图片转 PDF 工具

## 脚本调用

### 直接执行脚本
```bash
# 基本用法（原始质量）
python image-to-pdf/scripts/image_to_pdf.py scan.png

# 指定输出路径
python image-to-pdf/scripts/image_to_pdf.py scan.png --output doc.pdf

# 控制文件大小（尝试压缩到 1MB 以下）
python image-to-pdf/scripts/image_to_pdf.py scan.png --target-mb 1.0

# 固定 JPEG 品质
python image-to-pdf/scripts/image_to_pdf.py scan.png --jpeg-quality 85
```

### 从 Python 调用
```python
from image_to_pdf.scripts.image_to_pdf import image_to_pdf

# 基本用法
output = image_to_pdf("scan.png")

# 压缩到 1MB 以下
output = image_to_pdf("scan.png", target_mb=1.0)

# 固定 JPEG 品质
output = image_to_pdf("scan.png", jpeg_quality=85)
```

## 压缩策略

不指定 `--target-mb` 或 `--jpeg-quality` 时，保存原始质量 PDF。

指定参数时，算法自动尝试：
1. 先尝试缩小图片（shrink_factor 0~2）
2. 每个尺寸下尝试不同 JPEG 品质（92→85→75→...→25）
3. 返回第一个满足目标大小的组合；若无法满足，返回最小尺寸

## 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| image | str | - | 输入图片路径（必填） |
| --output | str | 自动 | 输出 PDF 路径，默认 `<原文件名>.pdf` |
| --target-mb | float | - | 目标文件大小（MB），自动压缩 |
| --jpeg-quality | int | - | 固定 JPEG 品质（1-100） |

## 注意事项

1. 自动处理含透明通道的图片
2. 非 RGB 色彩空间自动转换
3. 压缩时自动权衡分辨率和 JPEG 品质
4. 支持常见图片格式：png, jpg, jpeg, webp, bmp, tif, tiff 等
