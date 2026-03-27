#!/usr/bin/env python3
"""
检查微博 API 限流状态

用法:
    python3 check-rate-limit.py [--json]
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from common import check_token

WEIBO_API_BASE = "https://api.weibo.com/2"


def check_rate_limit(access_token: str) -> dict:
    import requests

    url = f"{WEIBO_API_BASE}/account/rate_limit_status.json"
    params = {"access_token": access_token}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}


def format_limit_info(data: dict) -> dict:
    if "error" in data:
        return data

    ip_limit = data.get("ip_limit", 15000)
    ip_remaining = data.get("ip_remaining", 0)
    user_limit = data.get("user_limit", 30)
    user_remaining = data.get("user_remaining", 0)
    reset_time = data.get("reset_time", 0)

    reset_time_str = None
    if reset_time:
        reset_time_str = datetime.fromtimestamp(reset_time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    ip_usage_pct = (
        ((ip_limit - ip_remaining) / ip_limit * 100) if ip_limit > 0 else 0
    )
    user_usage_pct = (
        ((user_limit - user_remaining) / user_limit * 100) if user_limit > 0 else 0
    )

    return {
        "ip_limit": ip_limit,
        "ip_remaining": ip_remaining,
        "ip_used": ip_limit - ip_remaining,
        "ip_usage_percent": round(ip_usage_pct, 2),
        "user_limit": user_limit,
        "user_remaining": user_remaining,
        "user_used": user_limit - user_remaining,
        "user_usage_percent": round(user_usage_pct, 2),
        "reset_time": reset_time_str,
    }


def print_limit_status(info: dict) -> None:
    if "error" in info:
        print(f"错误: {info['error']}")
        return

    print("=" * 60)
    print("微博 API 限流状态")
    print("=" * 60)

    print("\n【IP 级别限流】")
    print(f"  总配额: {info['ip_limit']:,} 次/小时")
    print(f"  已使用: {info['ip_used']:,} 次 ({info['ip_usage_percent']}%)")
    print(f"  剩余:   {info['ip_remaining']:,} 次")

    bar_width = 30
    filled = int(bar_width * info["ip_usage_percent"] / 100)
    bar = "█" * filled + "░" * (bar_width - filled)
    print(f"  [{bar}] {info['ip_usage_percent']}%")

    print("\n【用户级别限流】")
    print(f"  总配额: {info['user_limit']:,} 次/小时")
    print(f"  已使用: {info['user_used']:,} 次 ({info['user_usage_percent']}%)")
    print(f"  剩余:   {info['user_remaining']:,} 次")

    filled = int(bar_width * info["user_usage_percent"] / 100)
    bar = "█" * filled + "░" * (bar_width - filled)
    print(f"  [{bar}] {info['user_usage_percent']}%")

    if info["reset_time"]:
        print(f"\n限流重置时间: {info['reset_time']}")

    print("\n【发布限制说明】")
    print("  - 每小时最多发布 30 条微博")
    print("  - 单张图片最大 5MB")
    print("  - 文本长度最多 140 个中文字符")

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="检查微博 API 限流状态")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出")

    args = parser.parse_args()

    try:
        access_token = check_token()
    except ValueError as e:
        print(f"错误: {e}")
        print("\n请先获取 Access Token:")
        print("  1. python3 ../get-auth-url/scripts/get-auth-url.py")
        print("  2. python3 ../exchange-token/scripts/exchange-token.py <code>")
        sys.exit(1)

    try:
        data = check_rate_limit(access_token)

        if "error" in data:
            print(f"检查失败: {data['error']}")
            sys.exit(1)

        info = format_limit_info(data)

        if args.json:
            print(json.dumps(info, ensure_ascii=False, indent=2))
        else:
            print_limit_status(info)

    except Exception as e:
        print(f"检查失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
