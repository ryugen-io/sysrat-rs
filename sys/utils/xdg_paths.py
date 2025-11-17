#!/usr/bin/env python3
"""
XDG Base Directory specification utilities
"""

import os
from pathlib import Path


def get_xdg_state_home() -> Path:
    """
    Get XDG_STATE_HOME directory

    Returns $XDG_STATE_HOME or ~/.local/state if not set
    """
    xdg_state = os.getenv('XDG_STATE_HOME')
    if xdg_state:
        return Path(xdg_state)
    return Path.home() / '.local' / 'state'


def get_xdg_runtime_dir() -> Path | None:
    """
    Get XDG_RUNTIME_DIR directory

    Returns $XDG_RUNTIME_DIR or None if not set
    Should fallback to XDG_STATE_HOME if None
    """
    xdg_runtime = os.getenv('XDG_RUNTIME_DIR')
    if xdg_runtime:
        return Path(xdg_runtime)
    return None


def get_app_state_dir(app_name: str, create: bool = True) -> Path:
    """
    Get application state directory (for logs, history, etc.)

    Args:
        app_name: Application name (e.g., 'sysrat')
        create: Create directory if it doesn't exist

    Returns:
        Path to $XDG_STATE_HOME/{app_name}
    """
    state_dir = get_xdg_state_home() / app_name
    if create:
        state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


def get_app_runtime_dir(app_name: str, create: bool = True) -> Path:
    """
    Get application runtime directory (for PID files, sockets, etc.)

    Args:
        app_name: Application name (e.g., 'sysrat')
        create: Create directory if it doesn't exist

    Returns:
        Path to $XDG_RUNTIME_DIR/{app_name} or fallback to $XDG_STATE_HOME/{app_name}
    """
    runtime_dir = get_xdg_runtime_dir()

    if runtime_dir:
        app_runtime = runtime_dir / app_name
    else:
        # Fallback to state directory
        app_runtime = get_xdg_state_home() / app_name

    if create:
        app_runtime.mkdir(parents=True, exist_ok=True)

    return app_runtime


def get_log_file(app_name: str, config: dict) -> Path:
    """
    Get log file path with XDG fallback

    Priority:
    1. Explicit config LOG_FILE (absolute path)
    2. Explicit config LOG_FILE (relative to repo)
    3. XDG_STATE_HOME/{app_name}/server.log

    Args:
        app_name: Application name
        config: Config dict from load_env_config()

    Returns:
        Path to log file
    """
    # Check if LOG_FILE is explicitly set in config
    log_file_config = config.get('LOG_FILE', '')

    if log_file_config:
        log_path = Path(log_file_config)
        # If absolute path, use it directly
        if log_path.is_absolute():
            # Ensure parent directory exists
            log_path.parent.mkdir(parents=True, exist_ok=True)
            return log_path
        # If relative path starting with ./ or ../, resolve from repo root
        elif str(log_file_config).startswith(('./', '../')):
            # Caller should provide repo_root
            return log_path

    # Default: XDG_STATE_HOME/{app_name}/server.log
    state_dir = get_app_state_dir(app_name, create=True)
    return state_dir / 'server.log'


def get_pid_file(app_name: str, config: dict) -> Path:
    """
    Get PID file path with XDG fallback

    Priority:
    1. Explicit config PID_FILE (absolute path)
    2. Explicit config PID_FILE (relative to repo)
    3. XDG_RUNTIME_DIR/{app_name}/server.pid
    4. Fallback: XDG_STATE_HOME/{app_name}/server.pid

    Args:
        app_name: Application name
        config: Config dict from load_env_config()

    Returns:
        Path to PID file
    """
    # Check if PID_FILE is explicitly set in config
    pid_file_config = config.get('PID_FILE', '')

    if pid_file_config:
        pid_path = Path(pid_file_config)
        # If absolute path, use it directly
        if pid_path.is_absolute():
            # Ensure parent directory exists
            pid_path.parent.mkdir(parents=True, exist_ok=True)
            return pid_path
        # If relative path starting with ./ or ../, resolve from repo root
        elif str(pid_file_config).startswith(('./', '../')):
            # Caller should provide repo_root
            return pid_path

    # Default: XDG_RUNTIME_DIR/{app_name}/server.pid
    runtime_dir = get_app_runtime_dir(app_name, create=True)
    return runtime_dir / 'server.pid'
