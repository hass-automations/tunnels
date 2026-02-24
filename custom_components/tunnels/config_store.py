import os
import shutil

import config


def read_config() -> str:
    """Read config: prefer persistent path so UI shows what will survive restart."""
    for path in (config.VPN_CONFIG_PERSISTENT, config.VPN_CONFIG_PATH):
        try:
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
        except Exception as e:
            return f"# Failed to read config: {e}"
    return ""


def write_config(text: str) -> tuple[bool, str]:
    """Save to persistent path (addon_config) and sync to runtime path (used by VPN binary)."""
    if "[Interface]" not in text:
        return False, "Invalid config: missing [Interface] section"

    content = text.strip() + "\n"
    persistent = config.VPN_CONFIG_PERSISTENT
    runtime = config.VPN_CONFIG_PATH

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
