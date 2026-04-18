#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片标记工具 - 在图片上用绿色线框标记指定区域

使用方法:
    python mark_image.py <图片路径> <x1> <y1> <x2> <y2> [输出路径]

示例:
    python mark_image.py demo.png 100 200 300 400
    python mark_image.py demo.png 100 200 300 400 output.png

坐标说明:
    - 将图片的左上角视为 (0,0)，右下角视为 (1000, 1000)
    - 脚本会自动将坐标转换为实际像素位置
"""

import sys
from PIL import Image, ImageDraw


def mark_image(input_path, x1, y1, x2, y2, output_path=None):
    """
    在图片上用绿色线框标记指定区域

    Args:
        input_path: 输入图片路径
        x1, y1: 左上角坐标 (0-1000 范围)
        x2, y2: 右下角坐标 (0-1000 范围)
        output_path: 输出图片路径，默认为 input_path + "_marked.png"
    """
    # 打开图片
    img = Image.open(input_path)
    width, height = img.size

    # 将 0-1000 范围的坐标转换为实际像素坐标
    pixel_x1 = int((x1 / 1000) * width)
    pixel_y1 = int((y1 / 1000) * height)
    pixel_x2 = int((x2 / 1000) * width)
    pixel_y2 = int((y2 / 1000) * height)

    print(f"图片尺寸: {width} x {height}")
    print(f"输入坐标 (0-1000): [{x1}, {y1}, {x2}, {y2}]")
    print(f"转换后像素坐标: [{pixel_x1}, {pixel_y1}, {pixel_x2}, {pixel_y2}]")

    # 创建可绘制对象
    draw = ImageDraw.Draw(img)

    # 绘制绿色矩形框 (线宽 3 像素，颜色为亮绿色)
    # 确保坐标顺序正确 (左上角到右下角)
    left = min(pixel_x1, pixel_x2)
    top = min(pixel_y1, pixel_y2)
    right = max(pixel_x1, pixel_x2)
    bottom = max(pixel_y1, pixel_y2)

    draw.rectangle([left, top, right, bottom], outline="#00FF00", width=3)

    # 生成输出路径
    if output_path is None:
        # 在文件名后添加 _marked
        if "." in input_path:
            base, ext = input_path.rsplit(".", 1)
            output_path = f"{base}_marked.{ext}"
        else:
            output_path = f"{input_path}_marked.png"

    # 保存图片
    img.save(output_path)
    print(f"\n标记完成！输出文件: {output_path}")

    return output_path


def main():
    if len(sys.argv) < 6:
        print(__doc__)
        sys.exit(1)

    input_path = sys.argv[1]
    try:
        x1 = float(sys.argv[2])
        y1 = float(sys.argv[3])
        x2 = float(sys.argv[4])
        y2 = float(sys.argv[5])
    except ValueError:
        print("错误: 坐标必须是数字")
        sys.exit(1)

    # 验证坐标范围
    coords = [x1, y1, x2, y2]
    if any(c < 0 or c > 1000 for c in coords):
        print("错误: 坐标必须在 0-1000 范围内")
        sys.exit(1)

    output_path = sys.argv[6] if len(sys.argv) > 6 else None

    mark_image(input_path, x1, y1, x2, y2, output_path)


if __name__ == "__main__":
    main()
