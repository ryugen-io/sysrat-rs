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

from theme import (  # noqa: E402
    Colors, Icons, log_success, log_error, log_warn, log_info
)


def get_build_env() -> dict:
    """Get environment with verbose cargo build output enabled"""
    env = os.environ.copy()
    env['CARGO_BUILD_VERBOSE'] = '1'
    return env


def load_env_config(repo_root: Path) -> dict:
    """Load configuration from .env file"""
    config = {
        'SYS_DIR': '.sys',
        'GITHUB_DIR': '.github',
        'SCRIPT_DIRS': 'rust',
        'SERVER_BINARY': 'sysrat',
        'DISPLAY_NAME': 'sysrat',
        'SERVER_HOST': '10.1.1.30',
        'SERVER_PORT': '3000',
        'PID_FILE': '.server.pid',
        'LOG_FILE': 'server.log',
        'RUST_TOOLCHAIN': 'stable',
        'CARGO_AUDITABLE': 'true',
        'TRUNK_ENABLED': 'true',
        'SERVER_DIR': 'server',
        'FRONTEND_DIR': 'frontend',
        'CONFIG_FILE': 'sysrat.toml'
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
    log_info("Checking requirements...")

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
        log_error(f"Missing required tools: {', '.join(missing)}")
        print()
        print(f"{Colors.TEXT}Install with:{Colors.NC}")
        print(f"{Colors.BLUE}  cargo install {' '.join(missing)}{Colors.NC}")
        print()
        return False

    log_success("All required tools are available")
    return True


def check_config(config: dict) -> bool:
    """Validate configuration file"""
    config_file = REPO_ROOT / config['CONFIG_FILE']
    if not config_file.exists():
        log_error(f"{config['CONFIG_FILE']} not found")
        log_info(f"Please create {config['CONFIG_FILE']} with your configuration")
        return False

    log_info("Configuration file found")
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
    log_info("Stopping running servers...")

    pid_file = REPO_ROOT / config['PID_FILE']
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
                log_info(f"Stopping server with PID {old_pid}")
                subprocess.run(['kill', str(old_pid)], check=True,
                               capture_output=True)
                time.sleep(1)

                # Force kill if still running
                try:
                    subprocess.run(['kill', '-0', str(old_pid)], check=True,
                                   capture_output=True)
                    log_warn("Force killing server")
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
            log_info("Killing servers by name")
            subprocess.run(['pkill', '-f', server_binary], capture_output=True)
            time.sleep(1)
    except FileNotFoundError:
        pass

    # Verify port is free
    port = config['SERVER_PORT']
    if check_port(port):
        log_warn(f"Port {port} is still in use, waiting...")
        time.sleep(2)
        if check_port(port):
            log_error(f"Port {port} is still occupied")
            log_info("Manual intervention may be required")
            sys.exit(1)


def build_backend(config: dict, skip_format: bool = False) -> bool:
    """Build backend Rust code"""
    print()
    print(f"{Colors.BLUE}[rebuild]{Colors.NC} {Icons.HAMMER}  Building backend...")
    print()

    if not skip_format:
        log_info("Formatting backend code...")
        try:
            subprocess.run(['cargo', 'fmt', '--all'], cwd=REPO_ROOT,
                           check=True)
        except subprocess.CalledProcessError:
            log_error("Backend formatting failed")
            return False

    use_auditable = config.get('CARGO_AUDITABLE', 'true') == 'true'
    server_binary = config['SERVER_BINARY']

    log_info("Building backend (dev profile)...")
    try:
        if use_auditable:
            subprocess.run(['cargo', 'auditable', 'build', '--bin', server_binary],
                           cwd=REPO_ROOT, check=True, env=get_build_env())
        else:
            subprocess.run(['cargo', 'build', '--bin', server_binary],
                           cwd=REPO_ROOT, check=True, env=get_build_env())
    except subprocess.CalledProcessError:
        log_error("Backend dev build failed")
        return False

    log_info("Building backend (release profile)...")
    try:
        if use_auditable:
            subprocess.run(['cargo', 'auditable', 'build', '--release', '--bin', server_binary],
                           cwd=REPO_ROOT, check=True, env=get_build_env())
        else:
            subprocess.run(['cargo', 'build', '--release', '--bin', server_binary],
                           cwd=REPO_ROOT, check=True, env=get_build_env())
    except subprocess.CalledProcessError:
        log_error("Backend release build failed")
        return False

    print()
    log_success("Backend build successful")
    return True


def build_frontend(config: dict, skip_format: bool = False) -> bool:
    """Build frontend WASM code"""
    if config.get('TRUNK_ENABLED', 'true') != 'true':
        log_info("Frontend build disabled (TRUNK_ENABLED=false)")
        return True

    print()
    print(f"{Colors.BLUE}[rebuild]{Colors.NC} {Icons.HAMMER}  Building frontend...")
    print()

    frontend_dir = REPO_ROOT / config['FRONTEND_DIR']
    if not frontend_dir.exists():
        log_error(f"Frontend directory not found: {frontend_dir}")
        return False

    if not skip_format:
        log_info("Formatting frontend code...")
        try:
            subprocess.run(['cargo', 'fmt'], cwd=frontend_dir, check=True)
        except subprocess.CalledProcessError:
            log_error("Frontend formatting failed")
            return False

    log_info("Building WASM frontend (release)...")
    try:
        subprocess.run(['trunk', 'build', '--release'], cwd=frontend_dir,
                       check=True, env=get_build_env())
    except subprocess.CalledProcessError:
        log_error("Frontend release build failed")
        return False

    log_info("Building WASM frontend (dev)...")
    try:
        subprocess.run(['trunk', 'build'], cwd=frontend_dir, check=True,
                       env=get_build_env())
    except subprocess.CalledProcessError:
        log_error("Frontend dev build failed")
        return False

    print()
    log_success("Frontend build successful")
    return True


def start_server(config: dict) -> bool:
    """Start the server in background"""
    print()
    print(f"{Colors.MAUVE}[rebuild]{Colors.NC} {Icons.ROCKET}  Starting server...")
    print()

    log_file = REPO_ROOT / config['LOG_FILE']
    pid_file = REPO_ROOT / config['PID_FILE']
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
        log_error("Server failed to start")
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
        return False

    # Check if port is listening
    port = config['SERVER_PORT']
    max_attempts = 5
    for attempt in range(max_attempts):
        if check_port(port):
            print()
            log_success(f"Server running (PID: {server_pid})")
            print()
            log_info(f"URL: {Colors.SAPPHIRE}http://{config['SERVER_HOST']}:"
                     f"{port}{Colors.NC}")
            log_info(f"Logs: {Colors.BLUE}tail -f {log_file}{Colors.NC}")
            log_info(f"Stop: {Colors.BLUE}./stop.py{Colors.NC}")
            print()
            return True
        time.sleep(1)

    log_warn("Server process is running but port is not listening yet")
    log_info(f"Check logs with: tail -f {log_file}")
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
          f"Starting build process for {config['DISPLAY_NAME']}...")
    print()

    if not check_requirements(config):
        sys.exit(1)

    if not check_config(config):
        sys.exit(1)

    stop_servers(config)

    print()

    build_backend_flag = not args.frontend_only
    build_frontend_flag = not args.backend_only

    if build_backend_flag:
        if not build_backend(config, args.skip_format):
            sys.exit(1)

    if build_frontend_flag:
        if not build_frontend(config, args.skip_format):
            sys.exit(1)

    print()
    log_success("Build complete")
    print()

    if not args.no_server:
        if not start_server(config):
            sys.exit(1)
    else:
        print(f"{Colors.BLUE}[rebuild]{Colors.NC} Skipping server start "
              f"(--no-server flag)")
        print()


if __name__ == '__main__':
    main()
