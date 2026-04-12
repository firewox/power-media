"""
End-to-end test: validates isolated mode full workflow.
Requires manual execution and actual browser environment.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from virtual_desktop import VirtualDesktopManager
from isolated_browser import IsolatedBrowser
from isolated_operations import IsolatedOperation


def test_full_workflow():
    """Test complete isolated mode workflow"""
    print("=== Isolated Mode End-to-End Test ===\n")

    # 1. Initialize
    print("1. Initializing virtual desktop manager...")
    desktop_manager = VirtualDesktopManager()
    print(f"   Current desktop: {desktop_manager.get_current_desktop()}")
    print(f"   Desktop list: {desktop_manager.list_desktops()}\n")

    # 2. Initialize browser
    print("2. Initializing isolated browser...")
    browser = IsolatedBrowser(desktop_manager)

    try:
        hwnd = browser.setup()
        print(f"   Browser window hwnd: {hwnd}")
        print(f"   Isolated desktop ID: {browser.desktop_id}\n")

        # 3. Get window position
        print("3. Getting browser window position...")
        rect = browser.get_window_rect()
        print(f"   Position: {rect}\n")

        # 4. Test isolated operation
        print("4. Testing isolated operation (screenshot)...")

        def take_test_screenshot():
            import mss
            with mss.mss() as sct:
                shot = sct.grab(sct.monitors[0])
                return shot.size

        iso_op = IsolatedOperation(
            desktop_manager, browser, take_test_screenshot
        )
        result = iso_op.execute()
        print(f"   Screenshot size: {result}\n")

        # 5. Verify window on isolated desktop
        print("5. Verifying window on isolated desktop...")
        is_on_desktop = desktop_manager.is_window_on_current_desktop(
            browser.window_hwnd
        )
        print(f"   Window on isolated desktop: {is_on_desktop}\n")

        print("✅ Test passed!\n")

    except Exception as e:
        print(f"❌ Test failed: {e}\n")
        raise

    finally:
        # 6. Cleanup
        print("6. Cleaning up...")
        browser.cleanup()
        if browser.desktop_id:
            desktop_manager.cleanup([browser.desktop_id])
        print("   Cleanup complete")


if __name__ == "__main__":
    test_full_workflow()
