#!/usr/bin/env python3
"""
Session Manager - Task-based session tree management for multi-Agent collaboration.

Usage:
    python session-manager.py init-task --name "任务名称"
    python session-manager.py fork --agent "Agent A" --identity "身份" --name "会话名"
    python session-manager.py export --from <会话A> --to <会话B> --mode full|recent|file
    python session-manager.py board
    python session-manager.py tree
    python session-manager.py list [--session <会话名>]
    python session-manager.py update-status --agent "Agent A" --status completed
    python session-manager.py unregister --agent "Agent A"
"""

import argparse
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_project_root() -> Path:
    """Find project root (where .qwen/ exists)"""
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / ".qwen").exists():
            return parent
    # Fallback: use current directory
    return current


def get_sessions_dir() -> Path:
    """Get sessions directory"""
    return get_project_root() / ".qwen" / "sessions"


def find_current_task() -> Optional[Path]:
    """Find current task directory (most recently modified task)"""
    sessions_dir = get_sessions_dir()
    if not sessions_dir.exists():
        return None
    
    # Find directories starting with "task-"
    task_dirs = [d for d in sessions_dir.iterdir() 
                 if d.is_dir() and d.name.startswith("task-")]
    
    if not task_dirs:
        return None
    
    # Return most recently modified
    return max(task_dirs, key=lambda d: d.stat().st_mtime)


def parse_yaml_frontmatter(filepath: Path) -> dict:
    """Parse YAML frontmatter from markdown file"""
    if not filepath.exists():
        return {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not content.startswith('---'):
        return {}
    
    # Find second ---
    end_idx = content.find('---', 3)
    if end_idx == -1:
        return {}
    
    yaml_text = content[3:end_idx].strip()
    
    # Simple YAML parser (handles basic key-value and lists)
    result = {}
    current_key = None
    current_list = None
    current_dict_list = None
    
    for line in yaml_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Check for list item
        if line.startswith('- '):
            if current_dict_list:
                # Handle dict in list
                if ':' in line:
                    key_val = line[2:].split(':', 1)
                    key = key_val[0].strip()
                    val = key_val[1].strip().strip('"').strip("'")
                    if not current_dict_list or '___new_item___' in current_dict_list[-1]:
                        current_dict_list.append({key: val})
                    else:
                        current_dict_list[-1][key] = val
            elif current_list is not None:
                current_list.append(line[2:].strip().strip('"').strip("'"))
            continue
        
        # Check for key: value
        if ':' in line:
            key_val = line.split(':', 1)
            key = key_val[0].strip()
            val = key_val[1].strip()
            
            if not val:
                # This might be a list or dict list
                if key == 'refs':
                    current_dict_list = []
                    result[key] = current_dict_list
                    current_list = None
                elif key == 'exports':
                    current_dict_list = []
                    result[key] = current_dict_list
                    current_list = None
                else:
                    current_list = []
                    result[key] = current_list
                    current_dict_list = None
                current_key = key
            else:
                # Simple value
                val = val.strip('"').strip("'")
                result[key] = val
                current_list = None
                current_dict_list = None
                current_key = None
    
    return result


def write_yaml_frontmatter(filepath: Path, metadata: dict):
    """Write YAML frontmatter to markdown file"""
    lines = ['---']
    
    for key, value in metadata.items():
        if isinstance(value, list):
            if value and isinstance(value[0], dict):
                # List of dicts (refs, exports)
                lines.append(f'{key}:')
                for item in value:
                    lines.append(f'  - {list(item.items())[0][0]}: {list(item.items())[0][1]}')
                    for k, v in list(item.items())[1:]:
                        lines.append(f'    {k}: {v}')
            else:
                # Simple list
                lines.append(f'{key}:')
                for item in value:
                    lines.append(f'  - {item}')
        else:
            lines.append(f'{key}: {value}')
    
    lines.append('---\n')
    
    # Read existing content (if any)
    existing_content = ''
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Remove existing frontmatter
            if content.startswith('---'):
                end_idx = content.find('---', 3)
                if end_idx != -1:
                    existing_content = content[end_idx + 3:].strip()
            else:
                existing_content = content
    
    # Write new content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
        if existing_content:
            f.write('\n' + existing_content)


def cmd_init_task(args):
    """Initialize a new task"""
    task_name = args.name
    timestamp = datetime.now().strftime("%Y%m%d")
    task_id = f"task-{task_name.lower().replace(' ', '-').replace('_', '-')}-{timestamp}"
    
    sessions_dir = get_sessions_dir()
    task_dir = sessions_dir / task_id
    
    if task_dir.exists():
        print(f"❌ 错误：任务目录已存在: {task_dir}")
        sys.exit(1)
    
    # Create directories
    task_dir.mkdir(parents=True, exist_ok=True)
    
    # Create task-board.md
    board_file = task_dir / "task-board.md"
    board_metadata = {
        'task_name': task_name,
        'task_id': task_id,
        'created': datetime.now().isoformat(),
        'updated': datetime.now().isoformat()
    }
    write_yaml_frontmatter(board_file, board_metadata)
    
    # Add board content
    with open(board_file, 'a', encoding='utf-8') as f:
        f.write(f'\n# 任务面板：{task_name}\n\n')
        f.write('## Agent 列表\n\n')
    
    # Create main-session.md
    main_file = task_dir / "main-session.md"
    main_metadata = {
        'session_id': 'main-session',
        'session_name': task_name,
        'parent_task': task_id,
        'parent_session': None,
        'created': datetime.now().isoformat(),
        'updated': datetime.now().isoformat(),
        'status': 'active',
        'agent': 'current',
        'tags': [task_name]
    }
    write_yaml_frontmatter(main_file, main_metadata)
    
    with open(main_file, 'a', encoding='utf-8') as f:
        f.write(f'\n# {task_name}\n\n')
        f.write('## 会话目标\n\n')
        f.write('## 对话记录\n\n')
    
    print(f"✅ 任务已初始化: {task_id}")
    print(f"   路径: {task_dir}")
    print(f"   任务面板: {board_file}")
    return task_id


def cmd_fork(args):
    """Fork a sub-session and register Agent"""
    agent = args.agent
    identity = args.identity
    name = args.name
    
    task_dir = find_current_task()
    if not task_dir:
        print("❌ 错误：未找到当前任务，请先使用 init-task 初始化")
        sys.exit(1)
    
    # Create sub-session directory
    session_dir = task_dir / name
    session_dir.mkdir(parents=True, exist_ok=True)
    session_dir.mkdir(parents=True, exist_ok=True)
    
    # Create initial session file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    session_file = session_dir / f"{timestamp}_{name}.md"
    
    session_metadata = {
        'session_id': name,
        'session_name': identity,
        'parent_task': task_dir.name,
        'parent_session': 'main-session',
        'created': datetime.now().isoformat(),
        'updated': datetime.now().isoformat(),
        'status': 'active',
        'agent': agent,
        'tags': [identity]
    }
    write_yaml_frontmatter(session_file, session_metadata)
    
    with open(session_file, 'a', encoding='utf-8') as f:
        f.write(f'\n# {identity}\n\n')
        f.write('## 会话目标\n\n')
        f.write('## 对话记录\n\n')
    
    # Update task-board.md
    board_file = task_dir / "task-board.md"
    if board_file.exists():
        with open(board_file, 'a', encoding='utf-8') as f:
            f.write(f'\n### {agent}\n')
            f.write(f'- **身份**: {identity}\n')
            f.write(f'- **会话**: `{name}/`\n')
            f.write(f'- **状态**: working\n')
        
        # Update updated timestamp
        metadata = parse_yaml_frontmatter(board_file)
        metadata['updated'] = datetime.now().isoformat()
        # Re-write metadata (simplified)
        # In production, you'd want better YAML manipulation
        print(f"   ⚠️  任务面板已更新（Agent 注册）")
    
    print(f"✅ 子会话已创建: {name}")
    print(f"   路径: {session_dir}")
    print(f"   Agent: {agent} ({identity})")
    return name


def cmd_export(args):
    """Export session context"""
    from_session = args.from_session
    to_session = args.to
    mode = args.mode
    purpose = args.purpose or ""
    
    sessions_dir = get_sessions_dir()
    
    # Find source and target sessions
    # Search in current task first, then all sessions
    task_dir = find_current_task()
    if task_dir:
        from_dir = task_dir / from_session
        to_dir = task_dir / to_session
    
    if not from_dir.exists():
        # Search all sessions
        for session_dir in sessions_dir.iterdir():
            if session_dir.is_dir() and (session_dir / from_session).exists():
                from_dir = session_dir / from_session
                to_dir = session_dir / to_session
                break
    
    if not from_dir.exists():
        print(f"❌ 错误：源会话 '{from_session}' 不存在")
        sys.exit(2)
    
    if not to_dir.exists():
        # Create target directory
        to_dir.mkdir(parents=True, exist_ok=True)
    
    # Create refs directory in target
    refs_dir = to_dir / "refs"
    refs_dir.mkdir(parents=True, exist_ok=True)
    
    # Export based on mode
    exported_files = []
    
    if mode == 'full':
        # Export all .md files
        for md_file in from_dir.glob("*.md"):
            dest_file = refs_dir / f"from-{from_session}_{md_file.name}"
            _export_file(md_file, dest_file, from_session, to_session, purpose)
            exported_files.append(md_file.name)
    
    elif mode == 'recent':
        count = args.count or 3
        # Get all .md files sorted by modification time
        md_files = sorted(from_dir.glob("*.md"), 
                         key=lambda f: f.stat().st_mtime, 
                         reverse=True)
        
        for md_file in md_files[:count]:
            dest_file = refs_dir / f"from-{from_session}_{md_file.name}"
            _export_file(md_file, dest_file, from_session, to_session, purpose)
            exported_files.append(md_file.name)
    
    elif mode == 'file':
        if not args.file:
            print("❌ 错误：--file 参数是必须的（mode=file 时）")
            sys.exit(1)
        
        source_file = from_dir / args.file
        if not source_file.exists():
            print(f"❌ 错误：文件 '{args.file}' 在会话 '{from_session}' 中不存在")
            sys.exit(3)
        
        dest_file = refs_dir / f"from-{from_session}_{args.file}"
        _export_file(source_file, dest_file, from_session, to_session, purpose)
        exported_files.append(args.file)
    
    print(f"✅ 会话已导出: {from_session} → {to_session}")
    print(f"   模式: {mode}")
    print(f"   文件: {', '.join(exported_files)}")
    print(f"   用途: {purpose}")
    return exported_files


def _export_file(source: Path, dest: Path, from_session: str, to_session: str, purpose: str):
    """Export a single file with metadata header"""
    # Read source content
    with open(source, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already has frontmatter
    existing_metadata = {}
    body = content
    if content.startswith('---'):
        end_idx = content.find('---', 3)
        if end_idx != -1:
            body = content[end_idx + 3:].strip()
    
    # Create export metadata header
    export_metadata = {
        'exported_from': from_session,
        'exported_to': to_session,
        'exported_at': datetime.now().isoformat(),
        'purpose': purpose
    }
    
    # Write to destination
    write_yaml_frontmatter(dest, export_metadata)
    
    # Append body
    with open(dest, 'a', encoding='utf-8') as f:
        if body:
            f.write('\n' + body)


def cmd_board(args):
    """Display task board"""
    task_dir = find_current_task()
    if not task_dir:
        print("❌ 错误：未找到当前任务")
        sys.exit(1)
    
    board_file = task_dir / "task-board.md"
    if not board_file.exists():
        print("❌ 错误：任务面板不存在，请先初始化任务")
        sys.exit(1)
    
    # Read and display board
    with open(board_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    metadata = parse_yaml_frontmatter(board_file)
    task_name = metadata.get('task_name', task_dir.name)
    
    print(f"\n📋 任务面板：{task_name}")
    print("=" * 60)
    
    # Display content (skip frontmatter)
    if content.startswith('---'):
        end_idx = content.find('---', 3)
        if end_idx != -1:
            print(content[end_idx + 3:])
        else:
            print(content)
    else:
        print(content)
    print("=" * 60)


def cmd_tree(args):
    """Display session tree"""
    task_dir = find_current_task()
    if not task_dir:
        print("❌ 错误：未找到当前任务")
        sys.exit(1)
    
    print(f"\n📊 会话树：{task_dir.name}")
    print("=" * 60)
    
    # Find main session
    main_file = task_dir / "main-session.md"
    if main_file.exists():
        print("🟢 main-session")
        metadata = parse_yaml_frontmatter(main_file)
        print(f"   创建: {metadata.get('created', 'N/A')[:16]}")
    
    # Find sub-sessions
    for session_dir in sorted(task_dir.iterdir()):
        if not session_dir.is_dir():
            continue
        
        if session_dir.name in ['refs', 'archive']:
            continue
        
        # Check for session files
        md_files = list(session_dir.glob("*.md"))
        if not md_files:
            continue
        
        # Get metadata from first file
        metadata = parse_yaml_frontmatter(md_files[0])
        status_icon = "🟢" if metadata.get('status') == 'active' else "⚪"
        agent = metadata.get('agent', 'unknown')
        
        print(f"   ├── {status_icon} {session_dir.name}")
        print(f"   │   Agent: {agent}")
        print(f"   │   创建: {metadata.get('created', 'N/A')[:16]}")
        
        # Check for refs
        refs_dir = session_dir / "refs"
        if refs_dir.exists() and list(refs_dir.glob("*.md")):
            ref_count = len(list(refs_dir.glob("*.md")))
            print(f"   │   引用: {ref_count} 个会话")
    
    print("=" * 60)


def cmd_list(args):
    """List all sessions"""
    task_dir = find_current_task()
    if not task_dir:
        print("❌ 错误：未找到当前任务")
        sys.exit(1)
    
    print(f"\n📋 会话列表：{task_dir.name}\n")
    
    for session_dir in sorted(task_dir.iterdir()):
        if not session_dir.is_dir():
            continue
        
        md_files = list(session_dir.glob("*.md"))
        if not md_files:
            continue
        
        metadata = parse_yaml_frontmatter(md_files[0])
        status = "🟢" if metadata.get('status') == 'active' else "⚪"
        agent = metadata.get('agent', 'unknown')
        
        print(f"{status} {session_dir.name}")
        print(f"   Agent: {agent}")
        print(f"   状态: {metadata.get('status', 'unknown')}")
        print(f"   文件数: {len(md_files)}")
        
        if args.session and args.session != session_dir.name:
            continue
        
        # List files
        for md_file in md_files:
            print(f"   - {md_file.name}")
        
        print()


def cmd_update_status(args):
    """Update Agent status"""
    agent = args.agent
    status = args.status
    
    task_dir = find_current_task()
    if not task_dir:
        print("❌ 错误：未找到当前任务")
        sys.exit(1)
    
    board_file = task_dir / "task-board.md"
    if not board_file.exists():
        print("❌ 错误：任务面板不存在")
        sys.exit(1)
    
    # Read board content
    with open(board_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and update agent status
    import re
    pattern = rf'(### {agent}\n.*?- \*\*状态\*\*: )\w+'
    replacement = rf'\g<1>{status}'
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content == content:
        print(f"❌ 错误：未找到 Agent '{agent}'")
        sys.exit(1)
    
    with open(board_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Agent '{agent}' 状态已更新为: {status}")


def cmd_unregister(args):
    """Unregister an Agent"""
    agent = args.agent
    
    task_dir = find_current_task()
    if not task_dir:
        print("❌ 错误：未找到当前任务")
        sys.exit(1)
    
    board_file = task_dir / "task-board.md"
    if not board_file.exists():
        print("❌ 错误：任务面板不存在")
        sys.exit(1)
    
    # Read board content
    with open(board_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and remove agent section
    new_lines = []
    skip = False
    removed = False
    
    for i, line in enumerate(lines):
        if line.strip().startswith('### ') and agent in line:
            skip = True
            removed = True
            continue
        
        if skip:
            # Check if we hit next section
            if line.startswith('### ') or line.startswith('## '):
                skip = False
                new_lines.append(line)
            continue
        
        new_lines.append(line)
    
    if not removed:
        print(f"❌ 错误：未找到 Agent '{agent}'")
        sys.exit(1)
    
    with open(board_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✅ Agent '{agent}' 已注销")


def main():
    parser = argparse.ArgumentParser(
        description="Session Manager - Task-based session tree management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python session-manager.py init-task --name "isolated-mcp 测试"
  python session-manager.py fork --agent "Agent A" --identity "测试" --name testing
  python session-manager.py export --from testing --to dev --mode recent --count 3
  python session-manager.py board
  python session-manager.py tree
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # init-task
    init_parser = subparsers.add_parser("init-task", help="初始化新任务")
    init_parser.add_argument("--name", required=True, help="任务名称")
    
    # fork
    fork_parser = subparsers.add_parser("fork", help="Fork 子会话并注册 Agent")
    fork_parser.add_argument("--agent", required=True, help="Agent 标识")
    fork_parser.add_argument("--identity", required=True, help="Agent 身份（显示名）")
    fork_parser.add_argument("--name", required=True, help="子会话目录名")
    
    # export
    export_parser = subparsers.add_parser("export", help="导出会话上下文")
    export_parser.add_argument("--from", dest="from_session", required=True, help="源会话")
    export_parser.add_argument("--to", required=True, help="目标会话")
    export_parser.add_argument("--mode", required=True, choices=["full", "recent", "file"],
                              help="导出模式")
    export_parser.add_argument("--file", help="特定文件（mode=file 时必需）")
    export_parser.add_argument("--count", type=int, help="最近 N 个文件（mode=recent 时必需）")
    export_parser.add_argument("--purpose", default="", help="导出用途")
    
    # board
    subparsers.add_parser("board", help="查看任务面板")
    
    # tree
    subparsers.add_parser("tree", help="查看会话树")
    
    # list
    list_parser = subparsers.add_parser("list", help="列出所有会话")
    list_parser.add_argument("--session", help="过滤会话名")
    
    # update-status
    status_parser = subparsers.add_parser("update-status", help="更新 Agent 状态")
    status_parser.add_argument("--agent", required=True, help="Agent 标识")
    status_parser.add_argument("--status", required=True, 
                              choices=["active", "working", "completed", "idle"],
                              help="新状态")
    
    # unregister
    unregister_parser = subparsers.add_parser("unregister", help="注销 Agent")
    unregister_parser.add_argument("--agent", required=True, help="Agent 标识")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    commands = {
        'init-task': cmd_init_task,
        'fork': cmd_fork,
        'export': cmd_export,
        'board': cmd_board,
        'tree': cmd_tree,
        'list': cmd_list,
        'update-status': cmd_update_status,
        'unregister': cmd_unregister,
    }
    
    try:
        commands[args.command](args)
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
