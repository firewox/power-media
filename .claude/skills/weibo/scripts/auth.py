#!/usr/bin/env python3
"""
微博 OAuth2 认证模块

用法:
    python auth.py --get-url                    # 获取授权 URL
    python auth.py --exchange-code <code>       # 用 code 换取 Access Token
"""

import os
import sys
import argparse
import urllib.parse
from typing import Optional, Dict

import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 微博 API 配置
WEIBO_AUTH_URL = "https://api.weibo.com/oauth2/authorize"
WEIBO_TOKEN_URL = "https://api.weibo.com/oauth2/access_token"


class WeiboAuth:
    """微博 OAuth2 认证类"""

    def __init__(self, app_key: str, app_secret: str, redirect_uri: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri

    def get_authorize_url(self) -> str:
        """
        获取 OAuth2 授权 URL

        Returns:
            授权 URL，用户需要在浏览器中打开并授权
        """
        params = {
            "client_id": self.app_key,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
        }
        return f"{WEIBO_AUTH_URL}?{urllib.parse.urlencode(params)}"

    def exchange_code_for_token(self, code: str) -> Dict:
        """
        用授权码换取 Access Token

        Args:
            code: 用户授权后回调 URL 中的 code 参数

        Returns:
            包含 access_token, expires_in, uid 的字典

        Raises:
            requests.RequestException: API 请求失败
        """
        data = {
            "client_id": self.app_key,
            "client_secret": self.app_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
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

    def get_token_info(self, access_token: str) -> Dict:
        """
        获取 Access Token 的信息（用于验证 Token 有效性）

        Args:
            access_token: 访问令牌

        Returns:
            Token 信息字典
        """
        url = "https://api.weibo.com/oauth2/get_token_info"
        data = {"access_token": access_token}

        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}


def print_auth_instructions(auth_url: str):
    """打印授权指导信息"""
    print("=" * 60)
    print("微博 OAuth2 授权")
    print("=" * 60)
    print("\n请按以下步骤操作:")
    print("\n1. 在浏览器中打开以下 URL:")
    print(f"   {auth_url}")
    print("\n2. 登录微博账号并授权应用")
    print("\n3. 授权后，浏览器将跳转到回调地址，")
    print("   从 URL 中获取 'code' 参数值")
    print("   例如: https://yourdomain.com/callback?code=xxx")
    print("\n4. 运行以下命令换取 Access Token:")
    print("   python auth.py --exchange-code <code>")
    print("=" * 60)


def print_token_result(result: Dict):
    """打印 Token 获取结果"""
    print("=" * 60)
    print("Access Token 获取成功!")
    print("=" * 60)
    print(f"\nAccess Token: {result.get('access_token')}")
    print(f"过期时间: {result.get('expires_in')} 秒")
    print(f"用户 UID: {result.get('uid')}")
    print(f"\n请设置环境变量:")
    print(f'  export WEIBO_ACCESS_TOKEN="{result.get("access_token")}"')
    print("\n或将以下内容添加到 .env 文件:")
    print(f"WEIBO_ACCESS_TOKEN={result.get('access_token')}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="微博 OAuth2 认证工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python auth.py --get-url                    # 获取授权 URL
  python auth.py --exchange-code abc123       # 用 code 换取 Token
        """,
    )

    parser.add_argument(
        "--get-url",
        action="store_true",
        help="获取 OAuth2 授权 URL",
    )

    parser.add_argument(
        "--exchange-code",
        metavar="CODE",
        help="用授权码换取 Access Token",
    )

    parser.add_argument(
        "--check-token",
        metavar="TOKEN",
        help="检查 Access Token 信息",
    )

    args = parser.parse_args()

    # 检查环境变量
    app_key = os.getenv("WEIBO_APP_KEY")
    app_secret = os.getenv("WEIBO_APP_SECRET")
    redirect_uri = os.getenv("WEIBO_REDIRECT_URI")

    if not all([app_key, app_secret, redirect_uri]):
        print("错误: 缺少必需的环境变量")
        print("\n请设置以下环境变量:")
        print("  WEIBO_APP_KEY")
        print("  WEIBO_APP_SECRET")
        print("  WEIBO_REDIRECT_URI")
        print("\n或在项目根目录创建 .env 文件")
        sys.exit(1)

    auth = WeiboAuth(app_key, app_secret, redirect_uri)

    if args.get_url:
        auth_url = auth.get_authorize_url()
        print_auth_instructions(auth_url)

    elif args.exchange_code:
        try:
            result = auth.exchange_code_for_token(args.exchange_code)

            if "error" in result:
                print(f"错误: {result.get('error_description', result.get('error'))}")
                sys.exit(1)

            print_token_result(result)

        except requests.RequestException as e:
            print(f"请求失败: {e}")
            sys.exit(1)

    elif args.check_token:
        info = auth.get_token_info(args.check_token)
        print("Token 信息:")
        print(info)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
