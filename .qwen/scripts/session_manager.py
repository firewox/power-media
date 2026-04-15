"""
Session Tree Manager
会话树管理工具：创建、导出、挂载、查询会话

Usage:
    python session_manager.py create --name "会话名" --parent "父会话ID"
    python session_manager.py export --session "会话ID" --file "文件名" --target "目标会话ID"
    python session_manager.py mount --session "会话ID" --ref "引用文件路径"
    python session_manager.py tree                      # 显示会话树
    python session_manager.py list                      # 列出所有会话
"""

import argparse
import yaml
import os
import sys
from datetime import datetime
from pathlib import Path


class SessionManager:
    def __init__(self, base_path: str = ".qwen/sessions"):
        self.base_path = Path(base_path)
        self.tree_file = self.base_path / "session-tree.yaml"
        self.tree_data = self._load_tree()

    def _load_tree(self) -> dict:
        """加载会话树"""
        if self.tree_file.exists():
            with open(self.tree_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {"tree": {"root": "main", "branches": []}, "exports": [], "agent_assignments": []}

    def _save_tree(self):
        """保存会话树"""
        with open(self.tree_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.tree_data, f, allow_unicode=True, default_flow_style=False)

    def create_session(self, name: str, parent: str = None):
        """创建新会话"""
        session_id = name.lower().replace(" ", "-")
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        session_dir = self.base_path / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        # 创建会话元数据文件
        session_meta = {
            "session_id": session_id,
            "session_name": name,
            "parent_session": parent or "main",
            "created": datetime.now().isoformat(),
            "status": "active",
            "agent": "current",
            "tags": [],
            "refs": [],
            "children": []
        }

        meta_file = session_dir / f"{timestamp}_meta.yaml"
        with open(meta_file, 'w', encoding='utf-8') as f:
            yaml.dump(session_meta, f, allow_unicode=True)

        # 创建会话对话记录文件
        session_file = session_dir / f"{timestamp}_session.md"
        with open(session_file, 'w', encoding='utf-8') as f:
            f.write(f"# {name}\n\n")
            f.write(f"## 会话信息\n")
            f.write(f"- **创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"- **父会话**: {parent or 'main'}\n\n")
            f.write(f"## 对话记录\n\n")

        # 更新会话树
        branch = {
            "id": session_id,
            "name": name,
            "path": str(session_dir),
            "parent": parent or "main",
            "created": datetime.now().isoformat(),
            "status": "active",
            "children": []
        }

        self.tree_data["tree"]["branches"].append(branch)

        # 如果有父会话，添加到父会话的 children
        if parent:
            for branch_item in self.tree_data["tree"]["branches"]:
                if branch_item.get("id") == parent:
                    if "children" not in branch_item:
                        branch_item["children"] = []
                    branch_item["children"].append(session_id)
                    break

        self._save_tree()
        print(f"✅ 会话已创建: {session_id}")
        print(f"   路径: {session_dir}")
        print(f"   元数据: {meta_file}")
        return session_id

    def export_session_fragment(self, session_id: str, source_file: str, target_session: str, purpose: str = ""):
        """导出会话片段到目标会话"""
        source_dir = self.base_path / session_id
        source_file_path = source_dir / source_file

        if not source_file_path.exists():
            print(f"❌ 源文件不存在: {source_file_path}")
            return False

        # 读取源文件
        with open(source_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 创建导出文件
        target_dir = self.base_path / target_session
        target_dir.mkdir(parents=True, exist_ok=True)
        refs_dir = target_dir / "refs"
        refs_dir.mkdir(exist_ok=True)

        export_filename = f"from-{session_id}-{source_file}"
        export_file = refs_dir / export_filename

        # 添加元数据头
        export_meta = f"""---
exported_from: {session_id}
exported_file: {source_file}
exported_to: {target_session}
purpose: {purpose}
exported_at: {datetime.now().isoformat()}
---

"""
        with open(export_file, 'w', encoding='utf-8') as f:
            f.write(export_meta + content)

        # 记录导出
        export_record = {
            "id": f"export-{len(self.tree_data.get('exports', [])) + 1:03d}",
            "source_session": session_id,
            "source_file": source_file,
            "target_session": target_session,
            "exported_file": str(export_file),
            "purpose": purpose,
            "created": datetime.now().isoformat()
        }

        if "exports" not in self.tree_data:
            self.tree_data["exports"] = []
        self.tree_data["exports"].append(export_record)
        self._save_tree()

        print(f"✅ 会话片段已导出")
        print(f"   源: {session_id}/{source_file}")
        print(f"   目标: {target_session}/refs/{export_filename}")
        print(f"   用途: {purpose}")
        return True

    def mount_reference(self, session_id: str, ref_session_id: str, ref_file: str, purpose: str = ""):
        """挂载其他会话的内容作为参考"""
        # 导出并挂载
        return self.export_session_fragment(ref_session_id, ref_file, session_id, purpose)

    def show_tree(self):
        """显示会话树"""
        print("\n📊 会话树结构\n")
        print("=" * 60)

        branches = self.tree_data.get("tree", {}).get("branches", [])

        # 找到根节点
        root_id = self.tree_data.get("tree", {}).get("root", "main")
        root = next((b for b in branches if b.get("id") == root_id), None)

        if root:
            self._print_branch(root, branches, indent=0)

        print("=" * 60)

    def _print_branch(self, branch, all_branches, indent=0):
        """递归打印分支"""
        prefix = "  " * indent + ("└─ " if indent > 0 else "")
        status_icon = "🟢" if branch.get("status") == "active" else "⚪"
        print(f"{prefix}{status_icon} {branch.get('name', branch.get('id'))}")
        print(f"{'  ' * indent}   ID: {branch.get('id')}")
        print(f"{'  ' * indent}   创建: {branch.get('created', 'N/A')[:16]}")

        # 打印子节点
        children = branch.get("children", [])
        for child_id in children:
            child = next((b for b in all_branches if b.get("id") == child_id), None)
            if child:
                self._print_branch(child, all_branches, indent + 1)

    def list_sessions(self):
        """列出所有会话"""
        print("\n📋 会话列表\n")
        branches = self.tree_data.get("tree", {}).get("branches", [])

        for branch in branches:
            status = "🟢" if branch.get("status") == "active" else "⚪"
            parent = branch.get("parent", "main")
            print(f"{status} {branch.get('name', branch.get('id'))}")
            print(f"   ID: {branch.get('id')}")
            print(f"   父会话: {parent}")
            print(f"   路径: {branch.get('path')}")
            print(f"   创建: {branch.get('created', 'N/A')}")
            print()

    def show_exports(self):
        """显示所有导出记录"""
        print("\n📤 导出记录\n")
        exports = self.tree_data.get("exports", [])

        if not exports:
            print("   暂无导出记录\n")
            return

        for export in exports:
            print(f"📦 {export.get('id')}")
            print(f"   源: {export.get('source_session')}/{export.get('source_file')}")
            print(f"   目标: {export.get('target_session')}")
            print(f"   用途: {export.get('purpose', 'N/A')}")
            print(f"   时间: {export.get('created', 'N/A')[:16]}")
            print()


def main():
    parser = argparse.ArgumentParser(description="Session Tree Manager")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # create 命令
    create_parser = subparsers.add_parser("create", help="创建新会话")
    create_parser.add_argument("--name", required=True, help="会话名称")
    create_parser.add_argument("--parent", default=None, help="父会话ID")

    # export 命令
    export_parser = subparsers.add_parser("export", help="导出会话片段")
    export_parser.add_argument("--session", required=True, help="源会话ID")
    export_parser.add_argument("--file", required=True, help="源文件名")
    export_parser.add_argument("--target", required=True, help="目标会话ID")
    export_parser.add_argument("--purpose", default="", help="导出用途")

    # mount 命令
    mount_parser = subparsers.add_parser("mount", help="挂载其他会话的内容")
    mount_parser.add_argument("--session", required=True, help="目标会话ID")
    mount_parser.add_argument("--ref", required=True, help="引用的会话ID")
    mount_parser.add_argument("--file", required=True, help="引用的文件名")
    mount_parser.add_argument("--purpose", default="", help="挂载用途")

    # tree 命令
    subparsers.add_parser("tree", help="显示会话树")

    # list 命令
    subparsers.add_parser("list", help="列出所有会话")

    # exports 命令
    subparsers.add_parser("exports", help="显示导出记录")

    args = parser.parse_args()

    manager = SessionManager()

    if args.command == "create":
        manager.create_session(args.name, args.parent)
    elif args.command == "export":
        manager.export_session_fragment(args.session, args.file, args.target, args.purpose)
    elif args.command == "mount":
        manager.mount_reference(args.session, args.ref, args.file, args.purpose)
    elif args.command == "tree":
        manager.show_tree()
    elif args.command == "list":
        manager.list_sessions()
    elif args.command == "exports":
        manager.show_exports()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
