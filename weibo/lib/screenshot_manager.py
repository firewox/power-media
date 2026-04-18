#!/usr/bin/env python3
"""
Screenshot Manager - 截图管理器

处理截图的捕获、命名、存储和清理。
"""
import os
import shutil
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any


class ScreenshotError(Exception):
    """截图操作失败时抛出的异常"""
    pass


class ScreenshotManager:
    """
    截图管理器类

    功能：
    - 生成带时间戳的文件名
    - 确保目录存在
    - 保存截图（从源文件或 MCP 捕获）
    - 自动清理旧截图（可配置）
    - 目录大小监控
    - 列出所有截图
    """

    def __init__(
        self,
        base_dir: str = "screenshots/weibo/",
        max_age_days: int = 7
    ):
        """
        初始化截图管理器

        Args:
            base_dir: 截图存储基础目录，默认为 "screenshots/weibo/"
            max_age_days: 截图最大保留天数，默认为 7 天，0 或负数表示禁用清理
        """
        self.base_dir = base_dir
        self.max_age_days = max_age_days

        # 确保目录存在
        self._ensure_directory_exists()

    def _ensure_directory_exists(self) -> None:
        """确保截图目录存在"""
        try:
            os.makedirs(self.base_dir, exist_ok=True)
        except OSError as e:
            raise ScreenshotError(f"Failed to create directory {self.base_dir}: {e}")

    def generate_filename(self, context: str = "home") -> str:
        """
        生成带时间戳的文件名

        命名格式: weibo_{context}_{YYYYMMDD}_{HHMMSS}.png

        Args:
            context: 截图上下文，如 "home", "error", "login" 等

        Returns:
            生成的文件名（不含路径）

        Examples:
            >>> manager = ScreenshotManager()
            >>> manager.generate_filename("home")
            'weibo_home_20250419_143052.png'
            >>> manager.generate_filename("error")
            'weibo_error_20250419_143115.png'
        """
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        return f"weibo_{context}_{timestamp}.png"

    def save_screenshot(self, source_path: str, context: str = "home") -> str:
        """
        保存截图从源文件到管理目录

        Args:
            source_path: 源截图文件路径
            context: 截图上下文

        Returns:
            保存后的完整路径

        Raises:
            FileNotFoundError: 源文件不存在
            IOError: 读取或写入失败
            ScreenshotError: 其他截图相关错误
        """
        # 检查源文件是否存在
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source screenshot not found: {source_path}")

        if not os.path.isfile(source_path):
            raise FileNotFoundError(f"Source path is not a file: {source_path}")

        # 生成目标文件名
        filename = self.generate_filename(context)
        dest_path = os.path.join(self.base_dir, filename)

        try:
            # 复制文件
            shutil.copy2(source_path, dest_path)
        except IOError as e:
            raise IOError(f"Failed to copy screenshot from {source_path} to {dest_path}: {e}")
        except Exception as e:
            raise ScreenshotError(f"Unexpected error while saving screenshot: {e}")

        return dest_path

    def capture_and_save(
        self,
        mcp_client: Any,
        context: str = "home"
    ) -> str:
        """
        使用 MCP 客户端捕获并保存截图

        Args:
            mcp_client: MCP 客户端实例，需要有 inspect_screen() 方法
            context: 截图上下文

        Returns:
            保存后的完整路径

        Raises:
            ScreenshotError: MCP 调用失败或截图保存失败
            AttributeError: mcp_client 没有 inspect_screen 方法
        """
        # 检查 mcp_client 是否有 inspect_screen 方法
        if not hasattr(mcp_client, 'inspect_screen'):
            raise AttributeError(
                f"MCP client must have 'inspect_screen' method, got {type(mcp_client)}"
            )

        # 调用 MCP 捕获截图
        try:
            result = mcp_client.inspect_screen()
        except Exception as e:
            raise ScreenshotError(f"MCP inspect_screen call failed: {e}")

        # 检查结果
        if not isinstance(result, dict):
            raise ScreenshotError(f"MCP returned invalid result type: {type(result)}")

        if not result.get('success'):
            error_msg = result.get('error', 'Unknown error')
            raise ScreenshotError(f"MCP screenshot capture failed: {error_msg}")

        # 获取截图路径
        screenshot_path = result.get('screenshot_path')
        if not screenshot_path:
            raise ScreenshotError("MCP did not return screenshot_path")

        # 保存到管理目录
        try:
            saved_path = self.save_screenshot(screenshot_path, context)
        except (FileNotFoundError, IOError, ScreenshotError):
            # 直接向上抛出这些异常
            raise
        except Exception as e:
            raise ScreenshotError(f"Failed to save captured screenshot: {e}")

        return saved_path

    def cleanup_old_screenshots(self) -> int:
        """
        清理超过保留期限的旧截图

        Returns:
            删除的文件数量

        Note:
            如果 max_age_days <= 0，则禁用清理，返回 0
        """
        if self.max_age_days <= 0:
            return 0

        deleted_count = 0
        cutoff_time = time.time() - (self.max_age_days * 24 * 60 * 60)

        try:
            for filename in os.listdir(self.base_dir):
                # 只处理 .png 文件
                if not filename.endswith('.png'):
                    continue

                file_path = os.path.join(self.base_dir, filename)

                # 检查是否为文件
                if not os.path.isfile(file_path):
                    continue

                # 检查文件修改时间
                try:
                    file_mtime = os.path.getmtime(file_path)
                    if file_mtime < cutoff_time:
                        os.remove(file_path)
                        deleted_count += 1
                except OSError:
                    # 跳过无法访问的文件
                    continue

        except OSError:
            # 目录无法访问时返回 0
            pass

        return deleted_count

    def get_directory_size(self) -> int:
        """
        获取截图目录的总大小（字节）

        Returns:
            目录总大小，单位为字节
        """
        total_size = 0

        try:
            for dirpath, dirnames, filenames in os.walk(self.base_dir):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(file_path)
                    except OSError:
                        # 跳过无法访问的文件
                        continue
        except OSError:
            # 目录无法访问时返回 0
            pass

        return total_size

    def list_screenshots(self) -> List[Dict[str, Any]]:
        """
        列出所有截图文件

        Returns:
            截图文件信息列表，每个元素包含：
            - filename: 文件名
            - path: 完整路径
            - size: 文件大小（字节）
            - created_at: 创建时间（ISO 格式字符串）
            - modified_at: 修改时间（ISO 格式字符串）
            - context: 从文件名解析的上下文
        """
        screenshots = []

        try:
            for filename in sorted(os.listdir(self.base_dir)):
                # 只处理 .png 文件
                if not filename.endswith('.png'):
                    continue

                file_path = os.path.join(self.base_dir, filename)

                # 检查是否为文件
                if not os.path.isfile(file_path):
                    continue

                try:
                    stat = os.stat(file_path)

                    # 尝试从文件名解析上下文
                    context = self._parse_context_from_filename(filename)

                    screenshots.append({
                        'filename': filename,
                        'path': os.path.abspath(file_path),
                        'size': stat.st_size,
                        'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'context': context
                    })
                except OSError:
                    # 跳过无法访问的文件
                    continue

        except OSError:
            # 目录无法访问时返回空列表
            pass

        return screenshots

    def _parse_context_from_filename(self, filename: str) -> Optional[str]:
        """
        从文件名解析上下文

        格式: weibo_{context}_{YYYYMMDD}_{HHMMSS}.png

        Args:
            filename: 文件名

        Returns:
            上下文字符串，如果解析失败则返回 None
        """
        # 移除扩展名
        if filename.endswith('.png'):
            name = filename[:-4]
        else:
            name = filename

        parts = name.split('_')

        # 期望格式: ['weibo', context, date, time]
        if len(parts) >= 4 and parts[0] == 'weibo':
            # 上下文是第二部分（可能有多个下划线的情况）
            # 我们取索引 1 到 -3 的部分（排除 date 和 time）
            context_parts = parts[1:-2]
            return '_'.join(context_parts) if context_parts else None

        return None


if __name__ == "__main__":
    # 简单的自测代码
    import tempfile

    # 使用临时目录测试
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = ScreenshotManager(base_dir=tmpdir, max_age_days=7)

        print("Testing ScreenshotManager...")

        # 测试文件名生成
        filename = manager.generate_filename("test")
        print(f"Generated filename: {filename}")
        assert filename.startswith("weibo_test_")
        assert filename.endswith(".png")

        # 测试目录大小（空目录）
        size = manager.get_directory_size()
        print(f"Directory size (empty): {size} bytes")
        assert size == 0

        # 测试列出截图（空目录）
        screenshots = manager.list_screenshots()
        print(f"Screenshots (empty): {screenshots}")
        assert screenshots == []

        print("All basic tests passed!")