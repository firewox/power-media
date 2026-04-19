#!/usr/bin/env python3
"""
weibo-post-text-enhanced: 发布纯文本微博（增强版）

完整工作流程：
1. 解析命令行参数
2. 读取并验证内容文件
3. 初始化组件
4. 打开/聚焦微博窗口
5. 捕获并保存截图
6. 使用 Ollama Vision API 分析截图
7. 计算坐标并发送微博
8. 清理旧截图

使用方法:
    python post_text_enhanced.py --content-file content.txt
    python post_text_enhanced.py --content-file content.txt --model gemma3:4b-it-qat
    python post_text_enhanced.py --content-file content.txt --host http://192.168.1.100:11434
"""
import sys
import os
import json
import argparse
import re
import time

# 添加 lib 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))

from computer_mcp_client import WeiboAutomation
from screenshot_manager import ScreenshotManager, ScreenshotError

# 导入 ollama_vision 模块
ollama_vision_path = os.path.join(os.path.dirname(__file__), "../../../ollama_vision.py")
sys.path.insert(0, os.path.dirname(ollama_vision_path))
from ollama_vision import call_ollama, DEFAULT_PROMPT


class VisionAnalysisError(Exception):
    """视觉分析错误"""
    pass


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="发布纯文本微博（增强版）- 自动识别界面元素",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python post_text_enhanced.py --content-file content.txt
    python post_text_enhanced.py --content-file content.txt --model gemma3:4b-it-qat
    python post_text_enhanced.py --content-file content.txt --host http://192.168.1.100:11434
        """
    )

    parser.add_argument(
        "--content-file",
        required=True,
        help="包含微博内容的文件路径"
    )

    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="视觉分析的最大重试次数 (默认: 3)"
    )

    parser.add_argument(
        "--screenshot-dir",
        default="screenshots/weibo/",
        help="截图保存目录 (默认: screenshots/weibo/)"
    )

    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="禁用旧截图清理"
    )

    parser.add_argument(
        "--model",
        default="qwen3.5:397b-cloud",
        help="Ollama 模型名称 (默认: qwen3.5:397b-cloud)"
    )

    parser.add_argument(
        "--host",
        default="http://localhost:11434",
        help="Ollama API 地址 (默认: http://localhost:11434)"
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="API 请求超时时间（秒）(默认: 120)"
    )

    return parser.parse_args()


def read_content_file(file_path: str) -> str:
    """读取内容文件"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"内容文件不存在: {file_path}")

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"路径不是文件: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        return content
    except IOError as e:
        raise IOError(f"读取文件失败: {e}")


def validate_content(content: str) -> tuple:
    """验证微博内容"""
    if not content:
        return False, "内容不能为空"

    if len(content) > 140:
        return False, f"内容超长: {len(content)} 字符 (最多 140 字符)"

    return True, None


def parse_json_response(output: str) -> dict:
    """从模型输出中解析 JSON"""
    json_match = re.search(r'\{[\s\S]*\}', output)
    if json_match:
        json_str = json_match.group(0)
    else:
        json_str = output

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise VisionAnalysisError(f"JSON 解析失败: {e}")


def validate_coordinates(data: dict) -> dict:
    """验证坐标数据"""
    required_keys = ["input_box", "send_button"]
    result = {}

    for key in required_keys:
        if key not in data:
            raise VisionAnalysisError(f"缺少必需字段: {key}")

        value = data[key]
        if value is None:
            raise VisionAnalysisError(f"必需字段 '{key}' 不能为 null")

        if not isinstance(value, list) or len(value) != 4:
            raise VisionAnalysisError(f"'{key}' 格式错误，应为 [X1,Y1,X2,Y2]: {value}")

        coords = [float(v) for v in value]

        for i, v in enumerate(coords):
            if not (0.0 <= v <= 1.0):
                raise VisionAnalysisError(f"'{key}' 坐标超出范围 [0,1]: {v}")

        if coords[0] >= coords[2]:
            raise VisionAnalysisError(f"'{key}' X1 >= X2: {coords}")
        if coords[1] >= coords[3]:
            raise VisionAnalysisError(f"'{key}' Y1 >= Y2: {coords}")

        result[key] = coords

    result["headline_article_button"] = data.get("headline_article_button")

    return result


def analyze_screenshot(
    screenshot_path: str,
    model: str,
    host: str,
    max_retries: int = 3
) -> dict:
    """
    分析截图，返回元素坐标

    Args:
        screenshot_path: 截图文件路径
        model: Ollama 模型名称
        host: Ollama API 地址
        max_retries: 最大重试次数

    Returns:
        {
            "input_box": [X1, Y1, X2, Y2],
            "send_button": [X1, Y1, X2, Y2],
            "headline_article_button": [X1, Y1, X2, Y2] or None
        }
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            print(f"  分析尝试 {attempt + 1}/{max_retries}...")

            response = call_ollama(
                model=model,
                prompt=DEFAULT_PROMPT,
                image_path=screenshot_path,
                host=host,
                stream=False
            )

            content = response.get("message", {}).get("content", "")

            data = parse_json_response(content)
            result = validate_coordinates(data)

            print(f"  ✓ 分析成功")
            return result

        except VisionAnalysisError as e:
            last_error = e
            print(f"  ✗ 尝试 {attempt + 1} 失败: {e}")
            if attempt < max_retries - 1:
                delay = 2 ** attempt
                print(f"    等待 {delay}s 后重试...")
                time.sleep(delay)

        except Exception as e:
            last_error = e
            print(f"  ✗ 尝试 {attempt + 1} 异常: {e}")
            if attempt < max_retries - 1:
                delay = 2 ** attempt
                print(f"    等待 {delay}s 后重试...")
                time.sleep(delay)

    raise VisionAnalysisError(f"分析失败（已重试 {max_retries} 次）: {last_error}")


def main():
    """主函数"""
    print("=" * 60)
    print("发布纯文本微博（增强版）")
    print("=" * 60)

    # 1. 解析参数
    print("\n[1/8] 解析命令行参数...")
    try:
        args = parse_args()
        print(f"  内容文件: {args.content_file}")
        print(f"  模型: {args.model}")
        print(f"  API 地址: {args.host}")
        print(f"  最大重试次数: {args.max_retries}")
        print(f"  截图目录: {args.screenshot_dir}")
        print(f"  清理旧截图: {not args.no_cleanup}")
    except SystemExit as e:
        return {"success": False, "error": "参数解析失败"}

    # 2. 读取并验证内容
    print("\n[2/8] 读取并验证内容文件...")
    try:
        content = read_content_file(args.content_file)
        is_valid, error = validate_content(content)
        if not is_valid:
            result = {
                "success": False,
                "error": error,
                "content_file": args.content_file
            }
            print(f"  ✗ {error}")
            print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return result
        print(f"  ✓ 内容验证通过 ({len(content)} 字符)")
    except FileNotFoundError as e:
        result = {"success": False, "error": str(e), "content_file": args.content_file}
        print(f"  ✗ {e}")
        return result
    except IOError as e:
        result = {"success": False, "error": str(e), "content_file": args.content_file}
        print(f"  ✗ {e}")
        return result

    # 3. 初始化组件
    print("\n[3/8] 初始化组件...")
    try:
        weibo = WeiboAutomation()
        max_age_days = 0 if args.no_cleanup else 7
        screenshot_mgr = ScreenshotManager(
            base_dir=args.screenshot_dir,
            max_age_days=max_age_days
        )
        print("  ✓ WeiboAutomation 初始化完成")
        print(f"  ✓ ScreenshotManager 初始化完成 (目录: {args.screenshot_dir})")
    except Exception as e:
        result = {"success": False, "error": f"组件初始化失败: {e}", "content_file": args.content_file}
        print(f"  ✗ 初始化失败: {e}")
        return result

    # 4. 打开/聚焦微博窗口
    print("\n[4/8] 打开/聚焦微博窗口...")
    try:
        if not weibo.find_or_open_weibo():
            result = {
                "success": False,
                "error": "无法打开或找到微博窗口",
                "content_file": args.content_file,
                "content_length": len(content)
            }
            print("  ✗ 无法打开或找到微博窗口")
            return result
        print("  ✓ 微博窗口已就绪")
    except Exception as e:
        result = {"success": False, "error": f"打开微博窗口失败: {e}", "content_file": args.content_file}
        print(f"  ✗ 打开微博窗口失败: {e}")
        return result

    # 5. 捕获并保存截图
    print("\n[5/8] 捕获并保存截图...")
    try:
        screenshot_path = screenshot_mgr.capture_and_save(weibo.mcp, context="home")
        print(f"  ✓ 截图已保存: {screenshot_path}")
    except ScreenshotError as e:
        result = {"success": False, "error": f"截图失败: {e}", "content_file": args.content_file}
        print(f"  ✗ 截图失败: {e}")
        return result
    except Exception as e:
        result = {"success": False, "error": f"截图异常: {e}", "content_file": args.content_file}
        print(f"  ✗ 截图异常: {e}")
        return result

    # 6. Ollama Vision 分析截图
    print(f"\n[6/8] Ollama Vision 分析截图 (模型: {args.model})...")
    try:
        elements = analyze_screenshot(
            screenshot_path,
            model=args.model,
            host=args.host,
            max_retries=args.max_retries
        )
        print("  ✓ 界面元素识别完成")
        print(f"    - 输入框: {elements.get('input_box')}")
        print(f"    - 发送按钮: {elements.get('send_button')}")
        if elements.get('headline_article_button'):
            print(f"    - 头条文章按钮: {elements.get('headline_article_button')}")
    except VisionAnalysisError as e:
        result = {
            "success": False,
            "error": f"界面分析失败: {e}",
            "screenshot_path": screenshot_path,
            "content_file": args.content_file,
            "content_length": len(content)
        }
        print(f"  ✗ 界面分析失败: {e}")
        return result

    # 7. 计算坐标并发送微博
    print("\n[7/8] 计算坐标并发送微博...")
    try:
        window_rect = weibo.get_browser_window_rect()
        if not window_rect:
            result = {
                "success": False,
                "error": "无法获取浏览器窗口区域",
                "screenshot_path": screenshot_path,
                "elements_detected": elements,
                "content_file": args.content_file,
                "content_length": len(content)
            }
            print("  ✗ 无法获取浏览器窗口区域")
            return result

        print(f"  窗口区域: left={window_rect['left']}, top={window_rect['top']}, "
              f"width={window_rect['width']}, height={window_rect['height']}")

        from PIL import Image
        try:
            with Image.open(screenshot_path) as img:
                screenshot_width, screenshot_height = img.size
            print(f"  截图真实尺寸: width={screenshot_width}, height={screenshot_height}")
        except Exception as e:
            print(f"  警告: 无法读取截图尺寸，使用窗口尺寸: {e}")
            screenshot_width = window_rect['width']
            screenshot_height = window_rect['height']

        input_box_bbox = elements['input_box']
        send_button_bbox = elements['send_button']

        input_center = weibo.bbox_to_center(input_box_bbox)
        send_center = weibo.bbox_to_center(send_button_bbox)

        input_x, input_y = weibo.bbox_to_screen_coords(
            input_box_bbox, window_rect, screenshot_width, screenshot_height
        )
        send_x, send_y = weibo.bbox_to_screen_coords(
            send_button_bbox, window_rect, screenshot_width, screenshot_height
        )

        print(f"  输入框: bbox={input_box_bbox} -> center=({input_center[0]:.3f}, {input_center[1]:.3f}) "
              f"-> screen=({input_x}, {input_y})")
        print(f"  发送按钮: bbox={send_button_bbox} -> center=({send_center[0]:.3f}, {send_center[1]:.3f}) "
              f"-> screen=({send_x}, {send_y})")

        weibo.mcp.focus_window("微博")
        weibo.mcp.hotkey(["ctrl", "home"])
        weibo.mcp.wait(2)

        print("  点击输入框...")
        weibo.mcp.click(input_x, input_y)
        weibo.mcp.wait(1)

        print("  输入内容...")
        weibo.mcp.hotkey(["ctrl", "a"])
        weibo.mcp.wait(0.5)
        weibo.mcp.type_text(content)
        weibo.mcp.wait(1)

        print("  点击发送按钮...")
        weibo.mcp.click(send_x, send_y)
        weibo.mcp.wait(3)

        print("  ✓ 微博发送完成")

    except Exception as e:
        result = {
            "success": False,
            "error": f"发送微博失败: {e}",
            "screenshot_path": screenshot_path,
            "elements_detected": elements,
            "content_file": args.content_file,
            "content_length": len(content)
        }
        print(f"  ✗ 发送微博失败: {e}")
        return result

    # 8. 清理旧截图
    print("\n[8/8] 清理旧截图...")
    try:
        if args.no_cleanup:
            print("  ℹ 清理已禁用 (--no-cleanup)")
            deleted_count = 0
        else:
            deleted_count = screenshot_mgr.cleanup_old_screenshots()
            if deleted_count > 0:
                print(f"  ✓ 已清理 {deleted_count} 个旧截图")
            else:
                print("  ℹ 没有需要清理的旧截图")
    except Exception as e:
        print(f"  ⚠ 清理旧截图时出错: {e}")
        deleted_count = 0

    # 构建成功结果
    result = {
        "success": True,
        "message": "微博发送完成",
        "screenshot_path": screenshot_path,
        "elements_detected": {
            "input_box": input_box_bbox,
            "send_button": send_button_bbox,
            "headline_article_button": elements.get("headline_article_button")
        },
        "content_file": args.content_file,
        "content_length": len(content),
        "cleanup_deleted": deleted_count
    }

    print("\n" + "=" * 60)
    print("执行完成")
    print("=" * 60)
    print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")

    return result


if __name__ == "__main__":
    result = main()
    if not result.get("success"):
        sys.exit(1)
