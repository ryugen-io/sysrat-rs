#!/usr/bin/env python3
"""
Check the current status and stats of Rust server
"""

import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR
sys.path.insert(0, str(REPO_ROOT / 'sys' / 'theme'))
sys.path.insert(0, str(REPO_ROOT / 'sys' / 'utils'))

from theme import (  # noqa: E402
    Colors, Icons, log_success, log_error, log_info
)
from xdg_paths import get_log_file, get_pid_file  # noqa: E402


def load_env_config(repo_root: Path) -> dict:
    """Load configuration from .env file"""
    config = {
        'SYS_DIR': '.sys',
        'GITHUB_DIR': '.github',
        'SCRIPT_DIRS': 'rust',
        'SERVER_BINARY': 'sysrat',
        'DISPLAY_NAME': 'SysRat',
        'SERVER_HOST': '10.1.1.30',
        'SERVER_PORT': '3000',
        'PID_FILE': '.server.pid',
        'LOG_FILE': 'server.log'
    }

    sys_env_dir = repo_root / config['SYS_DIR'] / 'env'
    for env_name in ['.env', '.env.example']:
        env_file = sys_env_dir / env_name
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key] = value
            break

    return config


def log_stat(icon: str, label: str, value: str, color: str):
    """Log a statistic line"""
    print(f"{Colors.SUBTEXT}{icon:2}  {label:16}{Colors.NC} "
          f"{color}{value}{Colors.NC}")


def is_running(pid: int) -> bool:
    """Check if process is running"""
    try:
        subprocess.run(['kill', '-0', str(pid)], check=True,
                       capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def check_port(port: str) -> bool:
    """Check if port is in use"""
    try:
        result = subprocess.run(
            ['ss', '-ltn'],
            capture_output=True,
            text=True,
            check=True
        )
        return f":{port}" in result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            result = subprocess.run(
                ['lsof', '-i', f':{port}'],
                capture_output=True,
                text=True,
                check=True
            )
            return bool(result.stdout)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False


def get_process_start_time(pid: int) -> str:
    """Get process start time"""
    try:
        # Force English locale for consistent date parsing
        env = {'LC_ALL': 'C', 'LANG': 'C'}
        result = subprocess.run(
            ['ps', '-p', str(pid), '-o', 'lstart='],
            capture_output=True,
            text=True,
            check=True,
            env=env
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def calculate_uptime(start_time_str: str) -> str:
    """Calculate uptime from start time string"""
    try:
        # Parse start time (format: "Mon Nov 17 10:30:00 2025")
        start_time = datetime.strptime(start_time_str, "%a %b %d %H:%M:%S %Y")
        now = datetime.now()
        diff = int((now - start_time).total_seconds())

        days = diff // 86400
        hours = (diff % 86400) // 3600
        mins = (diff % 3600) // 60

        if days > 0:
            return f"{days}d {hours}h {mins}m"
        elif hours > 0:
            return f"{hours}h {mins}m"
        else:
            return f"{mins}m"
    except Exception:
        return "unknown"


def get_process_stats(pid: int) -> dict:
    """Get process CPU and memory stats"""
    stats = {'cpu': 'N/A', 'mem_pct': 'N/A', 'mem_size': 'N/A'}

    try:
        # Get CPU and memory percentage
        result = subprocess.run(
            ['ps', '-p', str(pid), '-o', '%cpu,%mem,rss'],
            capture_output=True,
            text=True,
            check=True
        )
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            parts = lines[1].strip().split()
            if len(parts) >= 3:
                stats['cpu'] = f"{parts[0]}%"
                stats['mem_pct'] = f"{parts[1]}%"
                # RSS is in KB, convert to MB
                rss_kb = int(parts[2])
                if rss_kb >= 1024:
                    stats['mem_size'] = f"{rss_kb / 1024:.1f} MB"
                else:
                    stats['mem_size'] = f"{rss_kb} KB"
    except (subprocess.CalledProcessError, ValueError, IndexError):
        pass

    return stats


def show_server_status(config: dict) -> bool:
    """Show detailed server status"""
    display_name = config['DISPLAY_NAME']
    server_binary = config['SERVER_BINARY']
    app_name = 'sysrat'
    port = config['SERVER_PORT']
    host = config['SERVER_HOST']

    # Get XDG-compliant paths
    pid_file = get_pid_file(app_name, config)
    log_file = get_log_file(app_name, config)

    # Handle relative paths from config
    if not pid_file.is_absolute():
        pid_file = REPO_ROOT / pid_file
    if not log_file.is_absolute():
        log_file = REPO_ROOT / log_file

    print(f"{Colors.MAUVE}{Icons.SERVER}  {display_name}{Colors.NC}")
    print()

    # Check PID file
    if not pid_file.exists():
        log_stat(Icons.STATUS, "Status:", "not running", Colors.RED)
        print()
        return False

    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
    except (ValueError, IOError):
        log_stat(Icons.STATUS, "Status:", "error (invalid PID file)", Colors.RED)
        print()
        return False

    # Check if process is running
    if not is_running(pid):
        log_stat(Icons.STATUS, "Status:", "not running", Colors.RED)
        print()
        return False

    # Process is running
    log_stat(Icons.STATUS, "Status:", "running", Colors.GREEN)
    log_stat(Icons.INFO, "PID:", str(pid), Colors.BLUE)

    # Get uptime
    start_time = get_process_start_time(pid)
    if start_time:
        uptime = calculate_uptime(start_time)
        log_stat(Icons.CLOCK, "Uptime:", uptime, Colors.GREEN)

    # Get CPU and memory stats
    stats = get_process_stats(pid)
    if stats['cpu'] != 'N/A':
        log_stat(Icons.CPU, "CPU:", stats['cpu'], Colors.BLUE)
    if stats['mem_size'] != 'N/A':
        mem_display = f"{stats['mem_size']}"
        if stats['mem_pct'] != 'N/A':
            mem_display += f" ({stats['mem_pct']})"
        log_stat(Icons.MEM, "Memory:", mem_display, Colors.YELLOW)

    # Check port
    if check_port(port):
        log_stat(Icons.NET, "Port:", f"{port} (listening)", Colors.GREEN)
        log_stat(Icons.INFO, "URL:", f"http://{host}:{port}", Colors.SAPPHIRE)
    else:
        log_stat(Icons.NET, "Port:", f"{port} (not listening)", Colors.RED)

    # Log file info
    if log_file.exists():
        log_size = log_file.stat().st_size
        size_kb = log_size / 1024
        if size_kb > 1024:
            size_str = f"{size_kb / 1024:.1f} MB"
        else:
            size_str = f"{size_kb:.1f} KB"
        log_stat(Icons.LOG, "Log file:", f"{log_file.name} ({size_str})", Colors.TEXT)

    print()
    return True


def main():
    """Main execution"""
    config = load_env_config(REPO_ROOT)
    display_name = config['DISPLAY_NAME']
    server_binary = config['SERVER_BINARY']
    host = config['SERVER_HOST']
    port = config['SERVER_PORT']

    print()
    print(f"{Colors.MAUVE}[status]{Colors.NC} {Icons.ROCKET}  "
          f"Checking {display_name} status...")
    print()

    if show_server_status(config):
        log_success("Server is running")
        print()
        # Get log file path for display
        app_name = 'sysrat'
        log_file = get_log_file(app_name, config)
        if not log_file.is_absolute():
            log_file = REPO_ROOT / log_file
        log_info(f"Logs: {Colors.BLUE}tail -f {log_file}{Colors.NC}")
        log_info(f"Stop: {Colors.BLUE}./stop.py{Colors.NC}")
    else:
        log_error("Server is not running")
        print()
        log_info(f"Start server with: {Colors.BLUE}./start.py{Colors.NC}")

    print()


if __name__ == '__main__':
    main()
