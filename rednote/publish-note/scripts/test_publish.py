#!/usr/bin/env python3
"""
测试发布小红书图文笔记 - 独立脚本
"""
import sys
import os
import time

# 添加 lib 到路径
lib_path = os.path.join(os.path.dirname(__file__), '..', '..', 'lib')
sys.path.insert(0, lib_path)

try:
    from rednote_automation import RedNoteAutomation
except ImportError:
    # 尝试其他路径
    lib_path2 = os.path.join(os.path.dirname(__file__), '..', 'lib')
    sys.path.insert(0, lib_path2)
    from rednote_automation import RedNoteAutomation

def main():
    print("=" * 60)
    print("测试发布小红书图文笔记")
    print("=" * 60)
    
    automation = RedNoteAutomation()
    
    # 步骤 1: 打开创作平台
    print("\n1. 打开创作平台...")
    if not automation.find_or_open_creator(page_type="creator"):
        print("无法打开创作平台")
        return
    
    # 步骤 2: 导航到发布页
    print("\n2. 导航到发布页...")
    automation.navigate_to(automation.PUBLISH_URL)
    time.sleep(5)
    
    # 步骤 3: 截图
    print("\n3. 截图...")
    result = automation.mcp.inspect_screen()
    print(f"截图路径: {result.get('screenshot_path')}")
    
    print("\n完成！请查看截图")

if __name__ == "__main__":
    main()
