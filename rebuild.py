#!/usr/bin/env python3
"""
Rebuild script for Rust server projects
Performs full build cycle: format, build backend and frontend, start server
"""

import sys
import subprocess
import time
import argparse
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR
sys.path.insert(0, str(REPO_ROOT / 'sys' / 'theme'))
sys.path.insert(0, str(REPO_ROOT / 'sys' / 'utils'))

from theme import (  # noqa: E402
    Colors, Icons, log_success, log_error, log_warn, log_info
)
from xdg_paths import get_log_file, get_pid_file  # noqa: E402


def get_build_env() -> dict:
    """Get environment with verbose cargo build output enabled"""
    env = os.environ.copy()
    env['CARGO_BUILD_VERBOSE'] = '1'
    return env


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
    required_keys = [
        'SERVER_BINARY', 'DISPLAY_NAME', 'SERVER_PORT',
        'SERVER_DIR', 'FRONTEND_DIR', 'RUST_TOOLCHAIN'
    ]
    missing = [key for key in required_keys if key not in config]
    if missing:
        raise ValueError(f"Missing required config keys in .env: {', '.join(missing)}")

    return config


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


def command_exists(cmd: str) -> bool:
    """Check if a command exists"""
    try:
        subprocess.run([cmd, '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def cargo_auditable_exists() -> bool:
    """Check if cargo auditable subcommand exists"""
    try:
        subprocess.run(['cargo', 'auditable', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_requirements(config: dict) -> bool:
    """Check if required tools are installed"""
    log_info("checking requirements...")

    missing = []

    if not command_exists('cargo'):
        missing.append('cargo')

    if config.get('TRUNK_ENABLED', 'true') == 'true':
        if not command_exists('trunk'):
            missing.append('trunk')

    if config.get('CARGO_AUDITABLE', 'true') == 'true':
        if not cargo_auditable_exists():
            missing.append('cargo-auditable')

    if missing:
        log_error(f"missing required tools: {', '.join(missing)}")
        print()
        print(f"{Colors.TEXT}install:{Colors.NC}")
        print(f"{Colors.BLUE}  cargo install {' '.join(missing)}{Colors.NC}")
        print()
        return False

    log_success("requirements met")
    return True


def check_config(config: dict) -> bool:
    """Validate configuration file"""
    config_file = REPO_ROOT / config['CONFIG_FILE']
    if not config_file.exists():
        log_error(f"{config['CONFIG_FILE']} not found")
        log_info(f"create {config['CONFIG_FILE']}")
        return False

    log_info("config found")
    return True


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


def stop_servers(config: dict):
    """Stop running servers"""
    log_info("stopping servers...")

    app_name = 'sysrat'
    pid_file = get_pid_file(app_name, config)
    server_binary = config['SERVER_BINARY']

    # Check PID file
    if pid_file.exists():
        try:
            with open(pid_file, 'r') as f:
                old_pid = int(f.read().strip())

            try:
                # Check if process exists
                subprocess.run(['kill', '-0', str(old_pid)], check=True,
                               capture_output=True)
                log_info(f"stopping pid {old_pid}")
                subprocess.run(['kill', str(old_pid)], check=True,
                               capture_output=True)
                time.sleep(1)

                # Force kill if still running
                try:
                    subprocess.run(['kill', '-0', str(old_pid)], check=True,
                                   capture_output=True)
                    log_warn("force killing server")
                    subprocess.run(['kill', '-9', str(old_pid)],
                                   capture_output=True)
                except subprocess.CalledProcessError:
                    pass  # Process already dead

            except subprocess.CalledProcessError:
                pass  # Process doesn't exist

            pid_file.unlink()
        except (ValueError, IOError):
            pass

    # Fallback: kill by name
    try:
        result = subprocess.run(['pgrep', '-f', server_binary],
                                capture_output=True, text=True)
        if result.returncode == 0:
            log_info("killing by name")
            subprocess.run(['pkill', '-f', server_binary], capture_output=True)
            time.sleep(1)
    except FileNotFoundError:
        pass

    # Verify port is free
    port = config['SERVER_PORT']
    if check_port(port):
        log_warn(f"port {port} still in use, waiting...")
        time.sleep(2)
        if check_port(port):
            log_error(f"port {port} still occupied")
            log_info("manual intervention required")
            sys.exit(1)


def build_backend(config: dict, skip_format: bool = False) -> bool:
    """Build backend Rust code"""
    print()
    print(f"{Colors.BLUE}[rebuild]{Colors.NC} {Icons.HAMMER}  building backend...")
    print()

    if not skip_format:
        log_info("formatting backend...")
        try:
            subprocess.run(['cargo', 'fmt', '--all'], cwd=REPO_ROOT,
                           check=True)
        except subprocess.CalledProcessError:
            log_error("backend formatting failed")
            return False

    use_auditable = config.get('CARGO_AUDITABLE', 'true') == 'true'
    server_binary = config['SERVER_BINARY']

    log_info("building backend dev...")
    try:
        if use_auditable:
            subprocess.run(['cargo', 'auditable', 'build', '--bin', server_binary],
                           cwd=REPO_ROOT, check=True, env=get_build_env())
        else:
            subprocess.run(['cargo', 'build', '--bin', server_binary],
                           cwd=REPO_ROOT, check=True, env=get_build_env())
    except subprocess.CalledProcessError:
        log_error("backend dev build failed")
        return False

    log_info("building backend release...")
    try:
        if use_auditable:
            subprocess.run(['cargo', 'auditable', 'build', '--release', '--bin', server_binary],
                           cwd=REPO_ROOT, check=True, env=get_build_env())
        else:
            subprocess.run(['cargo', 'build', '--release', '--bin', server_binary],
                           cwd=REPO_ROOT, check=True, env=get_build_env())
    except subprocess.CalledProcessError:
        log_error("backend release build failed")
        return False

    print()
    log_success("backend built")
    return True


def build_frontend(config: dict, skip_format: bool = False) -> bool:
    """Build frontend WASM code"""
    if config.get('TRUNK_ENABLED', 'true') != 'true':
        log_info("frontend disabled (TRUNK_ENABLED=false)")
        return True

    print()
    print(f"{Colors.BLUE}[rebuild]{Colors.NC} {Icons.HAMMER}  building frontend...")
    print()

    frontend_dir = REPO_ROOT / config['FRONTEND_DIR']
    if not frontend_dir.exists():
        log_error(f"frontend dir missing: {frontend_dir}")
        return False

    if not skip_format:
        log_info("formatting frontend...")
        try:
            subprocess.run(['cargo', 'fmt'], cwd=frontend_dir, check=True)
        except subprocess.CalledProcessError:
            log_error("frontend formatting failed")
            return False

    log_info("building frontend release...")
    try:
        subprocess.run(['trunk', 'build', '--release'], cwd=frontend_dir,
                       check=True, env=get_build_env())
    except subprocess.CalledProcessError:
        log_error("frontend release build failed")
        return False

    log_info("building frontend dev...")
    try:
        subprocess.run(['trunk', 'build'], cwd=frontend_dir, check=True,
                       env=get_build_env())
    except subprocess.CalledProcessError:
        log_error("frontend dev build failed")
        return False

    print()
    log_success("frontend built")
    return True


def start_server(config: dict) -> bool:
    """Start the server in background"""
    print()
    print(f"{Colors.MAUVE}[rebuild]{Colors.NC} {Icons.ROCKET}  starting server...")
    print()

    app_name = 'sysrat'
    log_file = get_log_file(app_name, config)
    pid_file = get_pid_file(app_name, config)
    server_binary = config['SERVER_BINARY']

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

    # Wait for server to start
    time.sleep(2)

    # Check if server is running
    if proc.poll() is not None:
        log_error("server failed to start")
        log_info("last 20 lines:")
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
        return False

    # Check if port is listening
    port = config['SERVER_PORT']
    max_attempts = 5
    for attempt in range(max_attempts):
        if check_port(port):
            print()
            log_success(f"server running (pid: {server_pid})")
            print()
            log_info(f"url: {Colors.SAPPHIRE}http://{get_display_host()}:"
                     f"{port}{Colors.NC}")
            log_info(f"logs: {Colors.BLUE}tail -f {log_file}{Colors.NC}")
            log_info(f"stop: {Colors.BLUE}./stop.py{Colors.NC}")
            print()
            return True
        time.sleep(1)

    log_warn("server running but port not ready")
    log_info(f"check logs: tail -f {log_file}")
    print()
    return True


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description='Rebuild script for Rust server projects',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--backend-only',
        action='store_true',
        help='Only build backend'
    )

    parser.add_argument(
        '--frontend-only',
        action='store_true',
        help='Only build frontend'
    )

    parser.add_argument(
        '--no-server',
        action='store_true',
        help="Don't start server after build"
    )

    parser.add_argument(
        '--skip-format',
        action='store_true',
        help='Skip code formatting'
    )

    args = parser.parse_args()

    config = load_env_config(REPO_ROOT)

    print()
    print(f"{Colors.MAUVE}[rebuild]{Colors.NC} {Icons.HAMMER}  "
          f"building {config['DISPLAY_NAME']}...")
    print()

    if not check_requirements(config):
        sys.exit(1)

    if not check_config(config):
        sys.exit(1)

    stop_servers(config)

    print()
    print(f"{Colors.SUBTEXT}{'─' * 40}{Colors.NC}")
    print()

    build_backend_flag = not args.frontend_only
    build_frontend_flag = not args.backend_only

    if build_backend_flag:
        if not build_backend(config, args.skip_format):
            sys.exit(1)
        print()
        print(f"{Colors.SUBTEXT}{'─' * 40}{Colors.NC}")
        print()

    if build_frontend_flag:
        if not build_frontend(config, args.skip_format):
            sys.exit(1)
        print()
        print(f"{Colors.SUBTEXT}{'─' * 40}{Colors.NC}")
        print()

    log_success("build complete")
    print()

    if not args.no_server:
        if not start_server(config):
            sys.exit(1)
    else:
        print(f"{Colors.BLUE}[rebuild]{Colors.NC} skipping server start "
              f"(--no-server flag)")
        print()


if __name__ == '__main__':
    main()
