#!/usr/bin/env python3
"""
Start Rust server
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
from xdg_paths import get_log_file, get_pid_file  # noqa: E402


def load_env_config(repo_root: Path) -> dict:
    """Load configuration from sys/env/.env file"""
    env_file = repo_root / 'sys' / 'env' / '.env'

    if not env_file.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {env_file}\n"
            f"Copy sys/env/.env.example to sys/env/.env and configure it."
        )

    config = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                # Remove quotes if present
                value = value.strip('"').strip("'")
                config[key] = value

    # Validate required keys
    required_keys = ['SERVER_BINARY', 'DISPLAY_NAME', 'SERVER_PORT']
    missing = [key for key in required_keys if key not in config]
    if missing:
        raise ValueError(f"Missing required config keys in .env: {', '.join(missing)}")

    return config


def is_running(pid: int) -> bool:
    """Check if process is running"""
    try:
        subprocess.run(['kill', '-0', str(pid)], check=True,
                       capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def get_display_host() -> str:
    """Get the primary IP address for display purposes"""
    import socket
    try:
        # Connect to external address to determine primary interface IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
    except OSError:
        return 'localhost'


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


def main():
    """Main execution function"""
    config = load_env_config(REPO_ROOT)
    server_binary = config['SERVER_BINARY']
    display_name = config['DISPLAY_NAME']
    app_name = 'sysrat'
    port = config['SERVER_PORT']
    display_host = get_display_host()

    # Get XDG-compliant paths
    pid_file = get_pid_file(app_name, config)
    log_file = get_log_file(app_name, config)

    # Handle relative paths from config
    if not pid_file.is_absolute():
        pid_file = REPO_ROOT / pid_file
    if not log_file.is_absolute():
        log_file = REPO_ROOT / log_file

    print()
    print(f"{Colors.MAUVE}[start]{Colors.NC} {Icons.ROCKET}  "
          f"Starting {display_name}...")
    print()

    # Check if already running via PID file
    if pid_file.exists():
        try:
            with open(pid_file, 'r') as f:
                old_pid = int(f.read().strip())

            if is_running(old_pid):
                log_warn(f"Server already running (PID: {old_pid})")
                print()
                log_info(f"URL: {Colors.SAPPHIRE}http://{display_host}:{port}{Colors.NC}")
                log_info(f"Logs: {Colors.BLUE}tail -f {log_file}{Colors.NC}")
                log_info(f"Stop: {Colors.BLUE}./stop.py{Colors.NC}")
                print()
                sys.exit(0)
            else:
                # PID file exists but process is dead
                pid_file.unlink()
        except (ValueError, IOError):
            pass

    log_info("Starting server...")

    # Remove old log file
    if log_file.exists():
        log_file.unlink()

    # Start server in background
    with open(log_file, 'w') as log:
        proc = subprocess.Popen(
            ['cargo', 'run', '--bin', server_binary],
            cwd=REPO_ROOT,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True
        )

    server_pid = proc.pid

    # Save PID to file
    with open(pid_file, 'w') as f:
        f.write(str(server_pid))

    time.sleep(2)

    # Check if server is running
    if proc.poll() is not None:
        log_error(f"Failed to start {display_name}")
        log_info("Last 20 lines of log:")
        print()
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                for line in lines[-20:]:
                    print(f"{Colors.RED}{line.rstrip()}{Colors.NC}")
        except IOError:
            print("No log file available")
        print()
        if pid_file.exists():
            pid_file.unlink()
        sys.exit(1)

    # Check if port is listening
    max_attempts = 5
    for attempt in range(max_attempts):
        if check_port(port):
            print()
            log_success(f"{display_name} is running (PID: {server_pid})")
            print()
            log_info(f"URL: {Colors.SAPPHIRE}http://{display_host}:{port}{Colors.NC}")
            log_info(f"Logs: {Colors.BLUE}tail -f {log_file}{Colors.NC}")
            log_info(f"Stop: {Colors.BLUE}./stop.py{Colors.NC}")
            print()
            print(f" {Colors.GREEN}{Icons.PLAY}{Colors.NC}  Done.")
            print()
            sys.exit(0)
        time.sleep(1)

    log_warn("Server process is running but port is not listening yet")
    log_info(f"Check logs with: tail -f {log_file}")
    print()
    sys.exit(0)


if __name__ == '__main__':
    main()
