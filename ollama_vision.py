#!/usr/bin/env python3
"""
Ollama Vision API Client

Usage:
    python ollama_vision.py --image path/to/image.png --prompt "What is in this image?"
    python ollama_vision.py --image path/to/image.png --prompt "Describe this" --model gemma4:e4b
"""

import argparse
import base64
import json
import sys
from pathlib import Path

import requests


DEFAULT_PROMPT = """请识别这张微博主页截图中的微博发文文本输入框、发送按钮、头条文章按钮，以纯JSON格式返回结果，无多余描述。

坐标使用归一化小数格式 [X1,Y1,X2,Y2]，数值范围 0~1，代表元素相对于整张图片的左上角与右下角位置。

返回格式：
{
  "input_box": [X1,Y1,X2,Y2],
  "send_button": [X1,Y1,X2,Y2],
  "headline_article_button": [X1,Y1,X2,Y2]
}

注意：
1. 只返回JSON，不要任何其他文字
2. 坐标必须是0-1之间的浮点数
3. [X1,Y1]是左上角，[X2,Y2]是右下角
4. 如果某个元素找不到，返回null
"""

def encode_image(image_path: str) -> str:
    """Encode image to base64 string."""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    return base64.b64encode(path.read_bytes()).decode()


def call_ollama(
    model: str,
    prompt: str,
    image_path: str = None,
    host: str = "http://localhost:11434",
    stream: bool = False,
) -> dict:
    """
    Call Ollama chat API.

    Args:
        model: Model name (e.g., "gemma4:e4b", "qwen2.5vl:7b")
        prompt: User prompt/message
        image_path: Optional path to image file
        host: Ollama API host
        stream: Enable streaming response

    Returns:
        API response dict
    """
    url = f"{host}/api/chat"

    messages = [
        {
            "role": "user",
            "content": prompt,
        }
    ]

    # Add image if provided
    if image_path:
        img_base64 = encode_image(image_path)
        messages[0]["images"] = [img_base64]

    payload = {
        "model": model,
        "messages": messages,
        "stream": stream,
    }

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        raise Exception(f"API error ({response.status_code}): {response.text}")

    return response.json()


def main():
    parser = argparse.ArgumentParser(
        description="Ollama Vision API Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Text only
    python ollama_vision.py --prompt "Hello, how are you?"

    # With image
    python ollama_vision.py --image screenshot.png --prompt "What is in this image?"

    # Specify model
    python ollama_vision.py --model gemma4:e4b --image photo.jpg --prompt "Describe this image"

    # Custom host
    python ollama_vision.py --host http://192.168.1.100:11434 --image test.png --prompt "Analyze"
        """,
    )

    parser.add_argument(
        "--model", "-m",
        default="qwen3.5:397b-cloud",
        help="Model name (default: qwen3.5:397b-cloud)"
    )

    parser.add_argument(
        "--prompt", "-p",
        required=False,
        default=DEFAULT_PROMPT,
        help="User prompt/message"
    )

    parser.add_argument(
        "--image", "-i",
        help="Path to image file (optional)"
    )

    parser.add_argument(
        "--host",
        default="http://localhost:11434",
        help="Ollama API host (default: http://localhost:11434)"
    )

    parser.add_argument(
        "--stream",
        action="store_true",
        help="Enable streaming response"
    )

    parser.add_argument(
        "--raw",
        action="store_true",
        help="Print raw JSON response"
    )

    args = parser.parse_args()

    # Validate image if provided
    if args.image and not Path(args.image).exists():
        print(f"Error: Image not found: {args.image}", file=sys.stderr)
        sys.exit(1)

    # Call API
    print(f"Model: {args.model}")
    if args.image:
        print(f"Image: {args.image}")
    print(f"Prompt: {args.prompt}")
    print("-" * 40)

    try:
        result = call_ollama(
            model=args.model,
            prompt=args.prompt,
            image_path=args.image,
            host=args.host,
            stream=args.stream,
        )

        if args.raw:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            content = result.get("message", {}).get("content", "")
            print(content)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
