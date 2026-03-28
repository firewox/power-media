#!/usr/bin/env python3
"""
用授权码换取微博 Access Token

用法:
    python3 exchange-token.py <code>
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from common import get_auth_config

WEIBO_TOKEN_URL = "https://api.weibo.com/oauth2/access_token"


def exchange_code_for_token(app_key: str, app_secret: str, redirect_uri: str, code: str) -> dict:
    import requests

    data = {
        "client_id": app_key,
        "client_secret": app_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        response = requests.post(
            WEIBO_TOKEN_URL,
            data=data,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        error_data = e.response.json() if e.response.text else {}
        error_msg = error_data.get("error_description", str(e))
        raise requests.RequestException(f"获取 Token 失败: {error_msg}")


def print_token_result(result: dict):
    print("=" * 60)
    print("Access Token 获取成功!")
    print("=" * 60)
    print(f"\nAccess Token: {result.get('access_token')}")
    print(f"过期时间: {result.get('expires_in')} 秒")
    print(f"用户 UID: {result.get('uid')}")
    print(f"\n请设置环境变量:")
    print(f'  export WEIBO_ACCESS_TOKEN="{result.get("access_token")}"')
    print("\n或将以下内容添加到项目根目录的 .env 文件:")
    print(f"WEIBO_ACCESS_TOKEN={result.get('access_token')}")
    print("\n现在你可以发布微博了:")
    print('  python3 ../post-text/scripts/post-text.py "Hello Weibo!"')
    print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print("用法: python3 exchange-token.py <code>")
        print("\n示例:")
        print("  python3 exchange-token.py abc123")
        print("\n说明:")
        print("  code 是从授权回调 URL 中获取的授权码")
        print("  例如: https://yourdomain.com/callback?code=abc123")
        sys.exit(1)

    code = sys.argv[1]

    try:
        config = get_auth_config()
    except ValueError as e:
        print(f"错误: {e}")
        print("\n请设置以下环境变量:")
        print("  WEIBO_APP_KEY")
        print("  WEIBO_APP_SECRET")
        print("  WEIBO_REDIRECT_URI")
        sys.exit(1)

    try:
        import requests
        result = exchange_code_for_token(
            config["app_key"],
            config["app_secret"],
            config["redirect_uri"],
            code
        )

        if "error" in result:
            print(f"错误: {result.get('error_description', result.get('error'))}")
            sys.exit(1)

        print_token_result(result)

    except ImportError:
        print("错误: 缺少 requests 模块")
        print("请运行: pip3 install requests")
        sys.exit(1)
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
