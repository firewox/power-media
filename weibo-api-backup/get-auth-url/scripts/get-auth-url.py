#!/usr/bin/env python3
"""
获取微博 OAuth2 授权 URL

用法:
    python3 get-auth-url.py
"""

import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from common import get_auth_config

WEIBO_AUTH_URL = "https://api.weibo.com/oauth2/authorize"


def get_authorize_url(app_key: str, redirect_uri: str) -> str:
    params = {
        "client_id": app_key,
        "redirect_uri": redirect_uri,
        "response_type": "code",
    }
    return f"{WEIBO_AUTH_URL}?{urllib.parse.urlencode(params)}"


def print_auth_instructions(auth_url: str):
    print("=" * 60)
    print("微博 OAuth2 授权")
    print("=" * 60)
    print("\n请按以下步骤操作:")
    print("\n1. 在浏览器中打开以下 URL:")
    print(f"   {auth_url}")
    print("\n2. 登录微博账号并授权应用")
    print("\n3. 授权后，浏览器将跳转到回调地址，")
    print("   从 URL 中获取 'code' 参数值")
    print("   例如: https://yourdomain.com/callback?code=abc123")
    print("\n4. 运行以下命令换取 Access Token:")
    print("   python3 ../exchange-token/scripts/exchange-token.py abc123")
    print("=" * 60)


def main():
    try:
        config = get_auth_config()
    except ValueError as e:
        print(f"错误: {e}")
        print("\n请设置以下环境变量:")
        print("  WEIBO_APP_KEY")
        print("  WEIBO_APP_SECRET")
        print("  WEIBO_REDIRECT_URI")
        print("\n或在项目根目录创建 .env 文件:")
        print("  WEIBO_APP_KEY=your_app_key")
        print("  WEIBO_APP_SECRET=your_app_secret")
        print("  WEIBO_REDIRECT_URI=https://yourdomain.com/callback")
        sys.exit(1)

    auth_url = get_authorize_url(config["app_key"], config["redirect_uri"])
    print_auth_instructions(auth_url)


if __name__ == "__main__":
    main()
