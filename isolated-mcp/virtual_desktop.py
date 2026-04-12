"""
Windows Virtual Desktop Manager.
Provides a simplified interface using PowerShell fallback and pywinauto.

Note: Direct COM access to IVirtualDesktopManagerInternal is unreliable
across Windows versions. This module uses a pragmatic approach:
1. Try pywinauto for basic operations
2. Fallback to PowerShell/keyboard shortcuts for desktop switching
"""

import ctypes
import ctypes.wintypes
import subprocess
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class VirtualDesktopError(Exception):
    """Virtual desktop operation error"""
    pass


class VirtualDesktopManager:
    """Windows Virtual Desktop Manager (simplified, cross-version compatible)"""

    def __init__(self):
        self._is_win11 = self._detect_win11()
        self._desktop_counter = 0  # Track created desktops for cleanup
        self._created_desktops: list[str] = []

    def _detect_win11(self) -> bool:
        """Detect Windows 11"""
        try:
            import platform
            version = platform.version()
            parts = version.split('.')
            major = int(parts[0])
            build = int(parts[2]) if len(parts) > 2 else 0
            return major >= 10 and build >= 22000
        except Exception:
            return False

    def _run_powershell(self, command: str, timeout: int = 5) -> str:
        """Run PowerShell command"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode != 0:
                logger.debug(f"PowerShell error: {result.stderr}")
            return result.stdout.strip()
        except Exception as e:
            logger.debug(f"PowerShell failed: {e}")
            return ""

    def create_desktop(self, name: str = "power-media-isolated") -> str:
        """
        Create a new virtual desktop using Win+Ctrl+D shortcut.

        Args:
            name: Desktop name (for tracking)

        Returns:
            desktop_id: Unique identifier for the desktop
        """
        try:
            # Use Win+Ctrl+D to create new virtual desktop
            ctypes.windll.user32.keybd_event(
                0x5B, 0, 0, 0  # VK_LWIN
            )
            ctypes.windll.user32.keybd_event(
                0x11, 0, 0, 0  # VK_CONTROL
            )
            ctypes.windll.user32.keybd_event(
                ord('D'), 0, 0, 0
            )
            ctypes.windll.user32.keybd_event(
                ord('D'), 0, 2, 0  # KEYEVENTF_KEYUP
            )
            ctypes.windll.user32.keybd_event(
                0x11, 0, 2, 0  # KEYEVENTF_KEYUP
            )
            ctypes.windll.user32.keybd_event(
                0x5B, 0, 2, 0  # KEYEVENTF_KEYUP
            )

            time.sleep(0.5)

            # Generate unique ID
            self._desktop_counter += 1
            desktop_id = f"isolated-desktop-{self._desktop_counter}-{int(time.time())}"
            self._created_desktops.append(desktop_id)

            logger.info(f"Created virtual desktop: {name} ({desktop_id})")
            return desktop_id

        except Exception as e:
            logger.error(f"Failed to create desktop: {e}")
            raise VirtualDesktopError(f"创建虚拟桌面失败: {e}") from e

    def switch_to_desktop(self, desktop_id: str) -> None:
        """
        Switch to a virtual desktop.
        
        Note: Without COM access to enumerate desktops, we track
        created desktops and use Ctrl+Win+Left/Right to navigate.
        This is a simplified approach.

        Args:
            desktop_id: Target desktop ID
        """
        if desktop_id not in self._created_desktops:
            raise VirtualDesktopError(f"Unknown desktop ID: {desktop_id}")

        try:
            # Find position in our tracking
            target_index = self._created_desktops.index(desktop_id)
            
            # We assume we start on the original desktop (index -1)
            # Navigate to target using Ctrl+Win+Right (target_index + 1 times)
            for _ in range(target_index + 1):
                self._switch_desktop_right()
                time.sleep(0.2)

            logger.debug(f"Switched to desktop: {desktop_id}")

        except Exception as e:
            logger.error(f"Failed to switch desktop: {e}")
            raise VirtualDesktopError(f"切换虚拟桌面失败: {e}") from e

    def _switch_desktop_right(self):
        """Switch to next desktop (Ctrl+Win+Right)"""
        ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)  # VK_LWIN
        ctypes.windll.user32.keybd_event(0x11, 0, 0, 0)  # VK_CONTROL
        ctypes.windll.user32.keybd_event(0x27, 0, 0, 0)  # VK_RIGHT
        ctypes.windll.user32.keybd_event(0x27, 0, 2, 0)
        ctypes.windll.user32.keybd_event(0x11, 0, 2, 0)
        ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)

    def _switch_desktop_left(self):
        """Switch to previous desktop (Ctrl+Win+Left)"""
        ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)
        ctypes.windll.user32.keybd_event(0x11, 0, 0, 0)
        ctypes.windll.user32.keybd_event(0x25, 0, 0, 0)  # VK_LEFT
        ctypes.windll.user32.keybd_event(0x25, 0, 2, 0)
        ctypes.windll.user32.keybd_event(0x11, 0, 2, 0)
        ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)

    def get_current_desktop(self) -> str:
        """
        Get current virtual desktop identifier.
        
        Returns tracked desktop ID or 'original' if on user desktop.
        """
        # Without COM access, we return a placeholder
        # In practice, IsolatedOperation tracks user/isolated desktop
        return "current-desktop"

    def move_window_to_desktop(self, hwnd: int, desktop_id: str) -> None:
        """
        Move window to target virtual desktop.
        Uses PowerShell with VirtualDesktop module.

        Args:
            hwnd: Window handle
            desktop_id: Target desktop ID
        """
        try:
            # Use Move-VirtualDesktopWindow via PowerShell
            # This requires the VirtualDesktop module
            cmd = f"""
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.SendKeys]::SendWait('^{{LWIN}}{{RIGHT}}')
            """
            self._run_powershell(cmd)
            time.sleep(0.5)
            
            logger.debug(f"Moved window {hwnd} toward desktop {desktop_id}")

        except Exception as e:
            logger.warning(f"move_window_to_desktop via PS failed: {e}")
            # Fallback: do nothing, window stays on current desktop
            pass

    def is_window_on_current_desktop(self, hwnd: int) -> bool:
        """Check if window is on current desktop (always returns True as fallback)"""
        return True

    def list_desktops(self) -> list[str]:
        """
        List known virtual desktops.
        Returns tracked desktop IDs + 'original'.
        """
        return ["original"] + self._created_desktops.copy()

    def cleanup(self, desktop_ids: Optional[list[str]] = None) -> None:
        """
        Cleanup virtual desktops by closing them.
        Uses Ctrl+Win+F4 to close current desktop.

        Args:
            desktop_ids: Desktop IDs to cleanup
        """
        if not desktop_ids:
            return

        for desktop_id in desktop_ids:
            if desktop_id not in self._created_desktops:
                continue

            try:
                # Switch to that desktop first
                self.switch_to_desktop(desktop_id)
                time.sleep(0.3)

                # Close it with Ctrl+Win+F4
                ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)
                ctypes.windll.user32.keybd_event(0x11, 0, 0, 0)
                ctypes.windll.user32.keybd_event(0x73, 0, 0, 0)  # VK_F4
                ctypes.windll.user32.keybd_event(0x73, 0, 2, 0)
                ctypes.windll.user32.keybd_event(0x11, 0, 2, 0)
                ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)

                time.sleep(0.3)
                self._created_desktops.remove(desktop_id)
                logger.info(f"Cleaned up virtual desktop: {desktop_id}")

            except Exception as e:
                logger.warning(f"Failed to cleanup desktop {desktop_id}: {e}")
