#!/usr/bin/env python3
"""
发布纯文本微博

用法:
    python3 post-text.py "微博内容"
"""

import os
import sys
import json
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from common import WeiboAPIError, check_token

WEIBO_API_BASE = "https://api.weibo.com/2"
MAX_STATUS_LENGTH = 140


def validate_status(status: str) -> bool:
    if not status:
        raise ValueError("微博内容不能为空")

    if len(status) > MAX_STATUS_LENGTH:
        raise ValueError(f"微博内容过长（最大 {MAX_STATUS_LENGTH} 个字符）")

    return True


def post_text(access_token: str, status: str) -> dict:
    import requests

    validate_status(status)

    url = f"{WEIBO_API_BASE}/statuses/update.json"
    data = {
        "access_token": access_token,
        "status": urllib.parse.quote(status),
    }

    try:
        response = requests.post(url, data=data, timeout=30)

        if response.status_code != 200:
            error_data = response.json()
            error_code = str(error_data.get("error_code", ""))
            error_msg = error_data.get("error", "未知错误")
            raise WeiboAPIError(error_code, error_msg)

        data = response.json()
        weibo_id = data.get("id")
        user = data.get("user", {})
        uid = user.get("id")

        return {
            "success": True,
            "weibo_id": str(weibo_id) if weibo_id else None,
            "url": f"https://weibo.com/{uid}/{weibo_id}" if weibo_id and uid else None,
            "created_at": data.get("created_at"),
            "text": data.get("text"),
        }

    except requests.RequestException as e:
        raise WeiboAPIError("network", f"网络请求失败: {e}")


def main():
    if len(sys.argv) < 2:
        print("用法: python3 post-text.py \"微博内容\"")
        print("\n示例:")
        print('  python3 post-text.py "Hello Weibo!"')
        sys.exit(1)

    status = sys.argv[1]

    try:
        access_token = check_token()
    except ValueError as e:
        print(f"错误: {e}")
        print("\n请先获取 Access Token:")
        print("  1. python3 ../get-auth-url/scripts/get-auth-url.py")
        print("  2. python3 ../exchange-token/scripts/exchange-token.py <code>")
        sys.exit(1)

    try:
        print(f"正在发布微博: {status}")
        result = post_text(access_token, status)

        print("\n" + "=" * 60)
        print("发布成功!")
        print("=" * 60)
        print(f"微博 ID: {result['weibo_id']}")
        print(f"链接: {result['url']}")
        print(f"时间: {result['created_at']}")
        print("=" * 60)

        print(json.dumps(result, ensure_ascii=False, indent=2))

    except WeiboAPIError as e:
        print(f"\n错误 [{e.code}]: {e.message}")
        sys.exit(1)
    except ValueError as e:
        print(f"\n输入错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
