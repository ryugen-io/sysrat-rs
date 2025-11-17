#!/usr/bin/env python3
"""
Stop Rust server
"""

import sys
import subprocess
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR
sys.path.insert(0, str(REPO_ROOT / 'sys' / 'theme'))
sys.path.insert(0, str(REPO_ROOT / 'sys' / 'utils'))

from theme import (  # noqa: E402
    Colors, Icons, log_success, log_error, log_warn, log_info
)
from xdg_paths import get_pid_file  # noqa: E402


def load_env_config(repo_root: Path) -> dict:
    """Load configuration from .env file"""
    config = {
        'SYS_DIR': '.sys',
        'GITHUB_DIR': '.github',
        'SCRIPT_DIRS': 'rust',
        'SERVER_BINARY': 'sysrat',
        'DISPLAY_NAME': 'sysrat',
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


def is_running(pid: int) -> bool:
    """Check if process is running"""
    try:
        subprocess.run(['kill', '-0', str(pid)], check=True,
                       capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    """Main execution"""
    config = load_env_config(REPO_ROOT)
    server_binary = config['SERVER_BINARY']
    display_name = config['DISPLAY_NAME']
    app_name = 'sysrat'

    # Get XDG-compliant PID file path
    pid_file = get_pid_file(app_name, config)

    # Handle relative paths from config
    if not pid_file.is_absolute():
        pid_file = REPO_ROOT / pid_file

    print()
    print(f"{Colors.MAUVE}[stop]{Colors.NC} {Icons.STOP}  "
          f"Stopping {display_name}...")
    print()

    # Check PID file
    server_stopped = False
    if pid_file.exists():
        try:
            with open(pid_file, 'r') as f:
                old_pid = int(f.read().strip())

            if is_running(old_pid):
                log_info(f"Stopping server with PID {old_pid}")
                subprocess.run(['kill', str(old_pid)], check=True,
                               capture_output=True)
                time.sleep(1)

                # Force kill if still running
                if is_running(old_pid):
                    log_warn("Force killing server")
                    subprocess.run(['kill', '-9', str(old_pid)],
                                   capture_output=True)
                    time.sleep(1)

                if not is_running(old_pid):
                    server_stopped = True
                else:
                    log_error("Failed to stop server")
                    sys.exit(1)
            else:
                log_warn("PID file exists but process is not running")

            pid_file.unlink()

        except (ValueError, IOError) as e:
            log_error(f"Error reading PID file: {e}")
            pid_file.unlink()
    else:
        # Try to find and kill by name
        try:
            result = subprocess.run(['pgrep', '-f', server_binary],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                log_info(f"Found {len(pids)} running server(s), stopping...")
                subprocess.run(['pkill', '-f', server_binary],
                               capture_output=True)
                time.sleep(1)
                server_stopped = True
            else:
                log_warn(f"No running {display_name} found")
                print()
                sys.exit(0)
        except FileNotFoundError:
            log_warn(f"No running {display_name} found")
            print()
            sys.exit(0)

    if server_stopped:
        print()
        log_success(f"{display_name} stopped successfully")
    else:
        log_warn("Server may still be running")
        log_info(f"Check with: ps aux | grep {server_binary}")

    print()
    print(f" {Colors.RED}{Icons.STOP}{Colors.NC}  Done.")
    print()


if __name__ == '__main__':
    main()
