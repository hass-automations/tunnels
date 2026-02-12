import fcntl
import os
import subprocess
from datetime import datetime

import config


def parse_autostart_delay_seconds(default: int = 5, min_sec: int = 1, max_sec: int = 300) -> int:
    """Parse AUTOSTART_DELAY_SECONDS from env, clamped to [min_sec, max_sec]."""
    try:
        raw = os.getenv("AUTOSTART_DELAY_SECONDS", str(default)) or str(default)
        return max(min_sec, min(max_sec, int(raw)))
    except (ValueError, TypeError):
        return default


def run_cmd(cmd: list[str], timeout: int = 45) -> tuple[int, str]:
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = (res.stdout or "") + (res.stderr or "")
        return res.returncode, out.strip()
    except subprocess.TimeoutExpired:
        return 124, f"Timeout after {timeout}s: {' '.join(cmd)}"
    except Exception as e:
        return 255, f"Exception running {' '.join(cmd)}: {e}"


def locked():
    os.makedirs("/tmp", exist_ok=True)
    f = open(config.VPN_LOCK_PATH, "w")
    fcntl.flock(f, fcntl.LOCK_EX)
    return f


def write_last_action(action: str, ok: bool, output: str) -> None:
    os.makedirs("/data", exist_ok=True)
    ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    line = f"[{ts}] action={action} ok={ok} iface={config.VPN_INTERFACE}\n{output}\n\n"
    try:
        with open(config.LAST_ACTION_PATH, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass


def read_last_action(max_bytes: int = 12_000) -> str:
    try:
        with open(config.LAST_ACTION_PATH, "rb") as f:
            data = f.read()
        if len(data) > max_bytes:
            data = data[-max_bytes:]
        return data.decode("utf-8", errors="replace")
    except FileNotFoundError:
        return ""
    except Exception as e:
        return f"Failed to read last action log: {e}"
