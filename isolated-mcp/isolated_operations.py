"""
Isolated Operation Wrapper.
Automatically handles virtual desktop switching for all operations.
"""

import time
import functools
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

# Desktop switch delay (seconds)
SWITCH_DELAY = 0.1
RESTORE_DELAY = 0.05


class IsolatedOperation:
    """Isolated operation base class, auto-handles desktop switching"""

    def __init__(
        self,
        desktop_manager,
        browser,
        operation: Callable
    ):
        """
        Args:
            desktop_manager: VirtualDesktopManager instance
            browser: IsolatedBrowser instance
            operation: Actual operation function
        """
        self.desktop_manager = desktop_manager
        self.browser = browser
        self.operation = operation

    def execute(self, *args, **kwargs) -> Any:
        """
        Execute operation with automatic desktop switching.

        Flow:
        1. Record user desktop
        2. Switch to isolated desktop
        3. Restore window
        4. Execute operation
        5. Switch back to user desktop (always)
        """
        # 1. Record user desktop
        user_desktop = self.desktop_manager.get_current_desktop()

        try:
            # 2. Switch to isolated desktop
            logger.debug(
                f"Switching to isolated desktop: {self.browser.desktop_id}"
            )
            self.desktop_manager.switch_to_desktop(self.browser.desktop_id)
            time.sleep(SWITCH_DELAY)

            # 3. Ensure window is in foreground
            self.browser.ensure_restored()
            time.sleep(RESTORE_DELAY)

            # 4. Execute actual operation
            op_name = getattr(self.operation, '__name__', 'anonymous')
            logger.debug(f"Executing operation: {op_name}")
            result = self.operation(*args, **kwargs)

            return result

        finally:
            # 5. Switch back to user desktop (always)
            logger.debug(
                f"Switching back to user desktop: {user_desktop}"
            )
            try:
                self.desktop_manager.switch_to_desktop(user_desktop)
                time.sleep(SWITCH_DELAY / 2)
            except Exception as e:
                logger.error(
                    f"Failed to switch back to user desktop: {e}"
                )
                # Try once more
                try:
                    self.desktop_manager.switch_to_desktop(user_desktop)
                except Exception:
                    pass


def isolated_op(desktop_manager, browser):
    """
    Decorator: wrap normal operation as isolated operation.

    Usage:
        @isolated_op(desktop_manager, browser)
        def my_click(x, y):
            pyautogui.click(x, y)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            iso_op = IsolatedOperation(
                desktop_manager, browser, func
            )
            return iso_op.execute(*args, **kwargs)
        return wrapper
    return decorator
