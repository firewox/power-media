#!/usr/bin/env python3

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass


class WeiboAPIError(Exception):
    ERROR_CODES = {
        "21301": "认证失败，请检查 Access Token",
        "21327": "Access Token 已过期，需要重新授权",
        "20016": "发布太频繁，请稍后再试",
        "20017": "内容重复，请修改后重试",
        "20012": "内容过长，请控制在 140 字符以内",
        "10023": "超出 API 调用频率限制",
    }

    def __init__(self, code: str, message: str = None):
        self.code = code
        self.message = message or self.ERROR_CODES.get(code, f"未知错误: {code}")
        super().__init__(f"[{code}] {self.message}")


def check_token() -> str:
    token = os.getenv("WEIBO_ACCESS_TOKEN")
    if not token:
        raise ValueError("未设置 WEIBO_ACCESS_TOKEN 环境变量")
    return token


def get_auth_config() -> dict:
    app_key = os.getenv("WEIBO_APP_KEY")
    app_secret = os.getenv("WEIBO_APP_SECRET")
    redirect_uri = os.getenv("WEIBO_REDIRECT_URI")

    if not all([app_key, app_secret, redirect_uri]):
        raise ValueError(
            "缺少必需的环境变量: WEIBO_APP_KEY, WEIBO_APP_SECRET, WEIBO_REDIRECT_URI"
        )

    return {
        "app_key": app_key,
        "app_secret": app_secret,
        "redirect_uri": redirect_uri,
    }
