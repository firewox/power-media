#!/usr/bin/env python3
"""
weibo-post-text: 发布纯文本微博
自动打开默认浏览器，复用已登录状态发布微博
"""
import sys
import os
import json
import argparse

# 添加 lib 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))

from computer_mcp_client import WeiboAutomation


def validate_content(content: str) -> tuple:
    """
    验证微博内容
    返回: (是否有效, 错误信息)
    """
    if not content:
        return False, "内容不能为空"
    
    if len(content) > 140:
        return False, f"内容超长: {len(content)} 字符 (最多 140 字符)"
    
    return True, None


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="发布纯文本微博")
    parser.add_argument("content", help="微博内容")
    parser.add_argument("--force", action="store_true", help="跳过确认直接发布")
    
    args = parser.parse_args()
    
    content = args.content
    
    print("=" * 50)
    print("发布纯文本微博")
    print("=" * 50)
    
    # 验证内容
    print(f"\n内容: {content}")
    is_valid, error = validate_content(content)
    
    if not is_valid:
        result = {
            "success": False,
            "error": error
        }
        print(f"\n✗ {error}")
        print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result
    
    print(f"✓ 内容验证通过 ({len(content)} 字符)")
    
    # 如果不是强制模式，询问确认
    if not args.force:
        print("\n是否发布？")
        confirm = input("按 Enter 确认，输入 n 取消: ").strip().lower()
        if confirm == 'n':
            result = {
                "success": False,
                "error": "用户取消"
            }
            print("\n已取消")
            return result
    
    try:
        # 创建微博自动化实例
        weibo = WeiboAutomation()
        
        # 查找或打开微博窗口
        print("\n1. 查找或打开微博窗口...")
        if not weibo.find_or_open_weibo():
            result = {
                "success": False,
                "error": "无法打开微博窗口"
            }
            print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return result
        
        print("✓ 微博窗口已就绪")
        
        # 检查登录状态
        print("\n2. 检查登录状态...")
        status = weibo.check_login_status()
        
        if not status.get("loggedIn"):
            result = {
                "success": False,
                "error": "未登录，请先登录微博"
            }
            print("\n✗ 未登录，请先登录微博")
            print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return result
        
        print(f"✓ 已登录: {status.get('userName', '未知用户')}")
        
        # 发布微博
        print("\n3. 发布微博...")
        result = weibo.post_text_weibo(content)
        
        # 输出结果
        print("\n" + "=" * 50)
        if result.get("success"):
            print("✓ 发布成功")
            print(f"  {result.get('message', '')}")
        else:
            print("✗ 发布失败")
            print(f"  {result.get('error', '未知错误')}")
        print("=" * 50)
        
        print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        return result
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        print(f"\n✗ 执行出错: {e}")
        print(f"\n结果: {json.dumps(error_result, ensure_ascii=False, indent=2)}")
        return error_result


if __name__ == "__main__":
    result = main()
    
    # 如果失败，返回非零退出码
    if not result.get("success"):
        sys.exit(1)
