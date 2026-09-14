import fcntl
import hashlib
import os
import time

import config
import utils

APPLIED_HASH_PATH = "/data/applied_config.hash"


def _tools(protocol: str) -> tuple[str, str]:
    if protocol == "amneziawg":
        return "awg", "awg-quick"
    return "wg", "wg-quick"


def _awg_env() -> dict:
    env = os.environ.copy()
    env["WG_QUICK_USERSPACE_IMPLEMENTATION"] = "amneziawg-go"
    return env


def _cmd_env(protocol: str) -> dict | None:
    return _awg_env() if protocol == "amneziawg" else None


def _config_hash() -> str:
    try:
        with open(config.VPN_CONFIG_PATH, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return ""


def _read_applied_hash() -> str:
    try:
        with open(APPLIED_HASH_PATH) as f:
            return f.read().strip()
    except Exception:
        return ""


def _write_applied_hash(h: str) -> None:
    os.makedirs("/data", exist_ok=True)
    with open(APPLIED_HASH_PATH, "w") as f:
        f.write(h)


def _clear_applied_hash() -> None:
    try:
        os.remove(APPLIED_HASH_PATH)
    except Exception:
        pass


def vpn_is_up(protocol: str = "wireguard") -> bool:
    wg, _ = _tools(protocol)
    rc, _ = utils.run_cmd([wg, "show", config.VPN_INTERFACE], timeout=5, env=_cmd_env(protocol))
    return rc == 0


def vpn_handshake_age(protocol: str = "wireguard") -> int | None:
    """Seconds since the most recent peer handshake, or None if no handshake recorded."""
    wg, _ = _tools(protocol)
    rc, out = utils.run_cmd(
        [wg, "show", config.VPN_INTERFACE, "latest-handshakes"],
        timeout=5,
        env=_cmd_env(protocol),
    )
    if rc != 0 or not out.strip():
        return None
    now = int(time.time())
    min_age = None
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 2:
            try:
                ts = int(parts[1])
                if ts > 0:
                    age = now - ts
                    if min_age is None or age < min_age:
                        min_age = age
            except ValueError:
                pass
    return min_age


def vpn_diag(protocol: str = "wireguard") -> str:
    wg, _ = _tools(protocol)
    rc, out = utils.run_cmd([wg, "show", config.VPN_INTERFACE], timeout=5, env=_cmd_env(protocol))
    if rc != 0:
        return out or "(diagnostics failed / interface down)"
    return out


def vpn_ip_addr(protocol: str = "wireguard") -> str:
    rc, out = utils.run_cmd(
        ["ip", "-br", "addr", "show", "dev", config.VPN_INTERFACE], timeout=5
    )
    if rc != 0:
        return out or "(ip addr failed / interface down)"
    return out


def vpn_up(protocol: str = "wireguard") -> tuple[bool, str]:
    _, wg_quick = _tools(protocol)
    env = _cmd_env(protocol)
    lockf = utils.locked()
    try:
        if not os.path.exists(config.VPN_CONFIG_PATH):
            return False, f"Config not found: {config.VPN_CONFIG_PATH}"

        current_hash = _config_hash()
        if vpn_is_up(protocol):
            if current_hash == _read_applied_hash():
                return True, "Already up."
            # Config changed — restart with new config
            utils.run_cmd([wg_quick, "down", config.VPN_CONFIG_PATH], timeout=45, env=env)

        rc, out = utils.run_cmd([wg_quick, "up", config.VPN_CONFIG_PATH], timeout=45, env=env)
        if rc == 0:
            _write_applied_hash(current_hash)
        return rc == 0, out
    finally:
        try:
            fcntl.flock(lockf, fcntl.LOCK_UN)
            lockf.close()
        except Exception:
            pass


def vpn_down(protocol: str = "wireguard") -> tuple[bool, str]:
    _, wg_quick = _tools(protocol)
    env = _cmd_env(protocol)
    lockf = utils.locked()
    try:
        if not vpn_is_up(protocol):
            return True, "Already down."
        rc, out = utils.run_cmd([wg_quick, "down", config.VPN_CONFIG_PATH], timeout=45, env=env)
        if rc == 0:
            _clear_applied_hash()
        return rc == 0, out
    finally:
        try:
            fcntl.flock(lockf, fcntl.LOCK_UN)
            lockf.close()
        except Exception:
            pass
