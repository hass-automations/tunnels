import os

import config


def read_config(protocol: str = "wireguard") -> str:
    """Read persistent config for the given protocol."""
    persistent, _ = config.get_config_paths(protocol)
    try:
        if os.path.isfile(persistent):
            with open(persistent, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        return f"# Failed to read config: {e}"
    return ""


def write_config(text: str, protocol: str = "wireguard") -> tuple:
    """Save to persistent path only. vpn_up() copies it to runtime before start."""
    if "[Interface]" not in text:
        return False, "Invalid config: missing [Interface] section"

    content = text.strip() + "\n"
    persistent, _ = config.get_config_paths(protocol)

    os.makedirs(os.path.dirname(persistent), exist_ok=True)
    try:
        with open(persistent, "w", encoding="utf-8") as f:
            f.write(content)
        return True, "Config saved (persisted across restarts)"
    except Exception as e:
        return False, str(e)
