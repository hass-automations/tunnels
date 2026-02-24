from datetime import datetime

from flask import request

import config
import vpn_control


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
    if protocol != "wireguard":
        return {
            "protocol": protocol,
            "supported": False,
            "up": False,
            "interface": "",
            "config_path": "",
            "ip": "",
            "diag": f"{protocol}: backend not implemented",
            "ts_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        }

    up = vpn_control.vpn_is_up()
    return {
        "protocol": "wireguard",
        "supported": True,
        "up": up,
        "interface": config.VPN_INTERFACE,
        "config_path": config.VPN_CONFIG_PATH,
        "ip": vpn_control.vpn_ip_addr() if up else "",
        "diag": vpn_control.vpn_diag() if up else "",
        "ts_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }


def get_config_placeholder(protocol: str) -> str:
    return """[Interface]
PrivateKey = ...
Address = 10.0.0.2/24

[Peer]
PublicKey = ...
Endpoint = ...
AllowedIPs = 0.0.0.0/0
"""
