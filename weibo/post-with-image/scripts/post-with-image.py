#!/usr/bin/env python3
"""
发布带图片的微博

用法:
    python3 post-with-image.py "微博内容" "/path/to/image.jpg"
"""

import os
import sys
import json
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from common import WeiboAPIError, check_token

WEIBO_UPLOAD_BASE = "https://upload.api.weibo.com/2"
MAX_STATUS_LENGTH = 140
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_status(status: str) -> bool:
    if not status:
        raise ValueError("微博内容不能为空")

    if len(status) > MAX_STATUS_LENGTH:
        raise ValueError(f"微博内容过长（最大 {MAX_STATUS_LENGTH} 个字符）")

    return True


def validate_image(image_path: str) -> Path:
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"图片文件不存在: {image_path}")

    if not path.is_file():
        raise ValueError(f"路径不是文件: {image_path}")

    if path.stat().st_size > MAX_IMAGE_SIZE:
        raise ValueError(f"图片大小超过 5MB 限制")

    ext = path.suffix.lower()
    if ext not in [".jpg", ".jpeg", ".gif", ".png"]:
        raise ValueError(f"不支持的图片格式: {ext}，仅支持 JPG, GIF, PNG")

    return path


def post_with_image(access_token: str, status: str, image_path: str) -> dict:
    import requests

    validate_status(status)
    path = validate_image(image_path)

    url = f"{WEIBO_UPLOAD_BASE}/statuses/upload.json"

    with open(path, "rb") as f:
        files = {"pic": (path.name, f, f"image/{path.suffix.lstrip('.')}")}
        data = {
            "access_token": access_token,
            "status": urllib.parse.quote(status),
        }

        try:
            response = requests.post(url, data=data, files=files, timeout=60)

            if response.status_code != 200:
                error_data = response.json()
                error_code = str(error_data.get("error_code", ""))
                error_msg = error_data.get("error", "未知错误")
                raise WeiboAPIError(error_code, error_msg)

            data = response.json()
            weibo_id = data.get("id")
            user = data.get("user", {})
            uid = user.get("id")
            pics = data.get("pic_urls", [])
            pic_url = pics[0].get("thumbnail_pic", "") if pics else ""

            return {
                "success": True,
                "weibo_id": str(weibo_id) if weibo_id else None,
                "url": f"https://weibo.com/{uid}/{weibo_id}" if weibo_id and uid else None,
                "created_at": data.get("created_at"),
                "text": data.get("text"),
                "pic_url": pic_url,
            }

        except requests.RequestException as e:
            raise WeiboAPIError("network", f"网络请求失败: {e}")


def main():
    if len(sys.argv) < 3:
        print("用法: python3 post-with-image.py \"微博内容\" \"/path/to/image.jpg\"")
        print("\n示例:")
        print('  python3 post-with-image.py "分享美景" "./photo.jpg"')
        sys.exit(1)

    status = sys.argv[1]
    image_path = sys.argv[2]

    try:
        access_token = check_token()
    except ValueError as e:
        print(f"错误: {e}")
        print("\n请先获取 Access Token:")
        print("  1. python3 ../get-auth-url/scripts/get-auth-url.py")
        print("  2. python3 ../exchange-token/scripts/exchange-token.py <code>")
        sys.exit(1)

    try:
        print(f"正在发布带图片的微博...")
        print(f"内容: {status}")
        print(f"图片: {image_path}")

        result = post_with_image(access_token, status, image_path)

        print("\n" + "=" * 60)
        print("发布成功!")
        print("=" * 60)
        print(f"微博 ID: {result['weibo_id']}")
        print(f"链接: {result['url']}")
        print(f"图片: {result['pic_url']}")
        print(f"时间: {result['created_at']}")
        print("=" * 60)

        print(json.dumps(result, ensure_ascii=False, indent=2))

    except WeiboAPIError as e:
        print(f"\n错误 [{e.code}]: {e.message}")
        sys.exit(1)
    except (ValueError, FileNotFoundError) as e:
        print(f"\n输入错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
