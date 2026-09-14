from __future__ import annotations

import fcntl
import hashlib
import os
import re
import shutil
import time

import config
import utils

_RANGE_RE = re.compile(r"^(\d+)\s*-\s*(\d+)$")


def _preprocess_awg_config(text: str) -> str:
    """Normalize Amnezia app config for awg-quick:
    - Range values like '25-35' → midpoint integer (awg setconf requires integers)
    - Strip IPv6 AllowedIPs (ip6_tables absent in HA containers)
    - When AllowedIPs=0.0.0.0/0: inject Table=off + PostUp/PostDown manual routing
      to avoid 'sysctl src_valid_mark' which fails on HA's read-only /proc/sys
    """
    # Pass 1: find server IP and whether full default route is requested
    endpoint_ip = None
    has_full_route = False
    in_peer = False
    for raw in text.splitlines():
        s = raw.strip()
        if s == "[Peer]":
            in_peer = True
            continue
        if s.startswith("[") and s != "[Peer]":
            in_peer = False
            continue
        if in_peer and "=" in s:
            k, _, v = s.partition("=")
            k, v = k.strip().lower(), v.strip()
            if k == "endpoint":
                host = v.rsplit(":", 1)[0].strip("[]")
                if host:
                    endpoint_ip = host
            if k == "allowedips":
                if any(x.strip() in ("0.0.0.0/0", "0/0") for x in v.split(",")):
                    has_full_route = True

    # Manual routing injected when routing all traffic through VPN:
    #   1. Add specific host route for the VPN server via original gateway (prevents loop)
    #   2. Add default route via VPN interface (lower metric → higher priority)
    #   PostDown cleans up both routes, original default (higher metric) takes over again.
    inject_routing = has_full_route and endpoint_ip
    if inject_routing:
        srv = endpoint_ip
        post_up = (
            f"GW=$(ip route show default | awk '/via/ {{print $3; exit}}'); "
            f"ip route add {srv}/32 via $GW 2>/dev/null || true; "
            f"ip route add default dev %i metric 0"
        )
        post_down = (
            f"ip route del default dev %i metric 0 2>/dev/null || true; "
            f"ip route del {srv}/32 2>/dev/null || true"
        )

    # Pass 2: emit normalized config
    lines = []
    in_interface = False
    in_peer = False
    extras_emitted = False

    for raw in text.splitlines():
        s = raw.strip()

        if s == "[Interface]":
            in_interface, in_peer = True, False
            lines.append(raw)
            continue

        if s == "[Peer]":
            if in_interface and not extras_emitted and inject_routing:
                lines.append("Table = off")
                lines.append(f"PostUp = {post_up}")
                lines.append(f"PostDown = {post_down}")
                extras_emitted = True
            in_interface, in_peer = False, True
            lines.append(raw)
            continue

        if not s or s.startswith("#"):
            lines.append(raw)
            continue

        if "=" in s:
            key, _, value = s.partition("=")
            key_s, value = key.strip(), value.strip()

            # Resolve range values
            m = _RANGE_RE.match(value)
            if m:
                lo, hi = int(m.group(1)), int(m.group(2))
                value = str((lo + hi) // 2)

            # Drop IPv6 from AllowedIPs
            if key_s.lower() == "allowedips":
                ipv4 = [ip.strip() for ip in value.split(",") if ":" not in ip.strip()]
                if ipv4:
                    value = ", ".join(ipv4)

            lines.append(f"{key_s} = {value}")
            continue

        lines.append(raw)

    if in_interface and not extras_emitted and inject_routing:
        lines.append("Table = off")
        lines.append(f"PostUp = {post_up}")
        lines.append(f"PostDown = {post_down}")

    return "\n".join(lines) + "\n"


def _tools(protocol: str) -> tuple:
    if protocol == "amneziawg":
        return "awg", "awg-quick"
    return "wg", "wg-quick"


def _awg_env() -> dict:
    env = os.environ.copy()
    env["WG_QUICK_USERSPACE_IMPLEMENTATION"] = "amneziawg-go"
    return env


def _cmd_env(protocol: str) -> dict | None:
    return _awg_env() if protocol == "amneziawg" else None


def _applied_hash_path(protocol: str) -> str:
    return f"/data/applied_config_{protocol}.hash"


def _config_hash(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return ""


def _read_applied_hash(protocol: str) -> str:
    try:
        with open(_applied_hash_path(protocol)) as f:
            return f.read().strip()
    except Exception:
        return ""


def _write_applied_hash(protocol: str, h: str) -> None:
    os.makedirs("/data", exist_ok=True)
    with open(_applied_hash_path(protocol), "w") as f:
        f.write(h)


def _clear_applied_hash(protocol: str) -> None:
    try:
        os.remove(_applied_hash_path(protocol))
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


def vpn_up(protocol: str = "wireguard") -> tuple:
    _, wg_quick = _tools(protocol)
    env = _cmd_env(protocol)
    persistent, runtime = config.get_config_paths(protocol)
    lockf = utils.locked()
    try:
        if not os.path.exists(persistent):
            return False, f"Config not found: {persistent}"

        current_hash = _config_hash(persistent)
        if vpn_is_up(protocol):
            if current_hash == _read_applied_hash(protocol):
                return True, "Already up."
            utils.run_cmd([wg_quick, "down", runtime], timeout=45, env=env)

        if protocol == "amneziawg":
            # Kill any stale userspace daemon left from a failed previous start
            utils.run_cmd(["pkill", "-f", f"amneziawg-go {config.VPN_INTERFACE}"], timeout=5)

        # wg-quick/awg-quick require filename == interface name, so copy persistent → runtime.
        # For amneziawg, resolve Amnezia app range values (e.g. '25-35') to integers first.
        os.makedirs(os.path.dirname(runtime), exist_ok=True)
        with open(persistent, "r") as f:
            text = f.read()
        if protocol == "amneziawg":
            text = _preprocess_awg_config(text)
        with open(runtime, "w") as f:
            f.write(text)
        os.chmod(runtime, 0o600)

        rc, out = utils.run_cmd([wg_quick, "up", runtime], timeout=45, env=env)
        if rc == 0:
            _write_applied_hash(protocol, current_hash)
        return rc == 0, out
    finally:
        try:
            fcntl.flock(lockf, fcntl.LOCK_UN)
            lockf.close()
        except Exception:
            pass


def vpn_down(protocol: str = "wireguard") -> tuple:
    _, wg_quick = _tools(protocol)
    env = _cmd_env(protocol)
    _, runtime = config.get_config_paths(protocol)
    lockf = utils.locked()
    try:
        if not vpn_is_up(protocol):
            return True, "Already down."
        rc, out = utils.run_cmd([wg_quick, "down", runtime], timeout=45, env=env)
        if rc == 0:
            _clear_applied_hash(protocol)
        return rc == 0, out
    finally:
        try:
            fcntl.flock(lockf, fcntl.LOCK_UN)
            lockf.close()
        except Exception:
            pass
