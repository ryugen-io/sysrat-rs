"""
Central Theming Module for Python Scripts
Catppuccin Mocha color palette with Nerd Font icons
STYLECHECK_IGNORE - Python module, no shebang needed
PYLINTCHECK_IGNORE - Theme module, different formatting standards
"""

# Catppuccin Mocha color palette (24-bit true color)


class Colors:
    RED = '\033[38;2;243;139;168m'        # #f38ba8 - Errors
    GREEN = '\033[38;2;166;227;161m'      # #a6e3a1 - Success
    YELLOW = '\033[38;2;249;226;175m'     # #f9e2af - Warnings
    BLUE = '\033[38;2;137;180;250m'       # #89b4fa - Info
    MAUVE = '\033[38;2;203;166;247m'      # #cba6f7 - Headers
    SAPPHIRE = '\033[38;2;116;199;236m'   # #74c7ec - Success highlights
    TEXT = '\033[38;2;205;214;244m'       # #cdd6f4 - Normal text
    SUBTEXT = '\033[38;2;186;194;222m'    # #bac2de - Subtext/dimmed
    NC = '\033[0m'                         # No Color / Reset


# Nerd Font Icons


class Icons:
    CHECK = '\uf00c'      #
    CROSS = '\uf00d'      #
    WARN = '\uf071'       #
    INFO = '\uf05a'       #
    DOCKER = '\uf308'     #
    ROCKET = '\uf135'     #
    FOLDER = '\uf07b'     #
    QUESTION = '\uf128'   #
    CHART = '\uf200'      # 󰈙
    PLAY = '\uf04b'       #
    HAMMER = '\uf6e3'     #
    CLEAN = '\uf0c2'      #
    SERVER = '\uf233'     # 󰒋
    CONTAINER = '\uf1b2'  #
    CLOCK = '\uf64f'      # 󰥔
    MEM = '\uf538'        # 󰍛
    CPU = '\uf2db'        # 󰻠
    NET = '\uf6ff'        # 󰈀
    LOG = '\uf15c'        #
    FILE = '\uf15b'       #
    DATABASE = '\uf1c0'   #
    STOP = '\uf04d'       #
    RESTART = '\uf01e'    #
    STATUS = '\uf05a'     #


def log_success(msg: str):
    """Log success message with icon"""
    print(f"{Colors.GREEN}{Icons.CHECK}  {Colors.NC}{msg}")


def log_error(msg: str):
    """Log error message with icon"""
    import sys
    print(f"{Colors.RED}{Icons.CROSS}  {Colors.NC}{msg}", file=sys.stderr)


def log_warn(msg: str):
    """Log warning message with icon"""
    print(f"{Colors.YELLOW}{Icons.WARN}  {Colors.NC}{msg}")


def log_info(msg: str):
    """Log info message with icon"""
    print(f"{Colors.BLUE}{Icons.INFO}  {Colors.NC}{msg}")


def log_header(msg: str):
    """Log header message"""
    print(f"{Colors.MAUVE}{msg}{Colors.NC}")
