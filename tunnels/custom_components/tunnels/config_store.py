import os
import shutil

import config


def read_config(protocol: str = "wireguard") -> str:
    """Read config for the given protocol; prefer persistent path."""
    persistent, runtime = config.get_config_paths(protocol)
    for path in (persistent, runtime):
        try:
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
        except Exception as e:
            return f"# Failed to read config: {e}"
    return ""


def write_config(text: str, protocol: str = "wireguard") -> tuple:
    """Save to persistent path and sync to runtime path."""
    if "[Interface]" not in text:
        return False, "Invalid config: missing [Interface] section"

    content = text.strip() + "\n"
    persistent, runtime = config.get_config_paths(protocol)

    os.makedirs(os.path.dirname(persistent), exist_ok=True)
    os.makedirs(os.path.dirname(runtime), exist_ok=True)
    try:
        with open(persistent, "w", encoding="utf-8") as f:
            f.write(content)
        if persistent != runtime:
            shutil.copy2(persistent, runtime)
        return True, "Config saved (persisted across restarts)"
    except Exception as e:
        return False, str(e)
