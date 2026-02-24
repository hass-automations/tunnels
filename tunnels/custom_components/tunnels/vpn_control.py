import fcntl
import os

import config
import utils


def vpn_is_up() -> bool:
    rc, _ = utils.run_cmd(["wg", "show", config.VPN_INTERFACE], timeout=5)
    return rc == 0


def vpn_diag() -> str:
    rc, out = utils.run_cmd(["wg", "show", config.VPN_INTERFACE], timeout=5)
    if rc != 0:
        return out or "(diagnostics failed / interface down)"
    return out


def vpn_ip_addr() -> str:
    rc, out = utils.run_cmd(
        ["ip", "-br", "addr", "show", "dev", config.VPN_INTERFACE], timeout=5
    )
    if rc != 0:
        return out or "(ip addr failed / interface down)"
    return out


def vpn_up() -> tuple[bool, str]:
    lockf = utils.locked()
    try:
        if not os.path.exists(config.VPN_CONFIG_PATH):
            return False, f"Config not found: {config.VPN_CONFIG_PATH}"

        if vpn_is_up():
            return True, "Already up."

        rc, out = utils.run_cmd(
            ["wg-quick", "up", config.VPN_CONFIG_PATH], timeout=45
        )
        return rc == 0, out
    finally:
        try:
            fcntl.flock(lockf, fcntl.LOCK_UN)
            lockf.close()
        except Exception:
            pass


def vpn_down() -> tuple[bool, str]:
    lockf = utils.locked()
    try:
        if not vpn_is_up():
            return True, "Already down."

        rc, out = utils.run_cmd(
            ["wg-quick", "down", config.VPN_CONFIG_PATH], timeout=45
        )
        return rc == 0, out
    finally:
        try:
            fcntl.flock(lockf, fcntl.LOCK_UN)
            lockf.close()
        except Exception:
            pass
