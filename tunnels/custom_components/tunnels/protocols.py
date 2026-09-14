from datetime import datetime

from flask import request

import config
import vpn_control

SUPPORTED = {"wireguard", "amneziawg"}


def get_protocol_from_request() -> str:
    p = (
        request.args.get("protocol")
        or request.form.get("protocol")
        or config.DEFAULT_PROTOCOL
    ).strip().lower()
    if not any(x["id"] == p for x in config.PROTOCOLS):
        return "wireguard"
    return p


def proto_status(protocol: str) -> dict:
    if protocol not in SUPPORTED:
        return {
            "protocol": protocol,
            "supported": False,
            "up": False,
            "handshake_age_s": None,
            "interface": "",
            "config_path": "",
            "ip": "",
            "diag": f"{protocol}: backend not implemented",
            "ts_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        }

    up = vpn_control.vpn_is_up(protocol)
    return {
        "protocol": protocol,
        "supported": True,
        "up": up,
        "handshake_age_s": vpn_control.vpn_handshake_age(protocol) if up else None,
        "interface": config.VPN_INTERFACE,
        "config_path": config.VPN_CONFIG_PATH,
        "ip": vpn_control.vpn_ip_addr(protocol) if up else "",
        "diag": vpn_control.vpn_diag(protocol) if up else "",
        "ts_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }


def get_config_placeholder(protocol: str) -> str:
    if protocol == "amneziawg":
        return """[Interface]
PrivateKey = ...
Address = 10.8.1.5/24
Jc = 4
Jmin = 40
Jmax = 70
S1 = 0
S2 = 0
H1 = 1
H2 = 2
H3 = 3
H4 = 4

[Peer]
PublicKey = ...
Endpoint = ...
AllowedIPs = 10.8.1.0/24
PersistentKeepalive = 25
"""
    return """[Interface]
PrivateKey = ...
Address = 10.0.0.2/24

[Peer]
PublicKey = ...
Endpoint = ...
AllowedIPs = 0.0.0.0/0
"""
