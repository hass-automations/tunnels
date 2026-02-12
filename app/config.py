import os

from utils import parse_autostart_delay_seconds

# Protocol-agnostic VPN settings (WireGuard when DEFAULT_PROTOCOL=wireguard).
VPN_INTERFACE = os.getenv("VPN_INTERFACE", os.getenv("WG_INTERFACE", "wg0"))
# Runtime path used by wg-quick (inside container)
VPN_CONFIG_PATH = os.getenv(
    "VPN_CONFIG_PATH",
    os.getenv("WG_CONFIG_DST", f"/etc/wireguard/{VPN_INTERFACE}.conf"),
)
# Persistent path (addon_config, survives restart)
VPN_CONFIG_PERSISTENT = os.getenv(
    "WG_CONFIG_SRC",
    os.getenv("VPN_CONFIG_PERSISTENT", VPN_CONFIG_PATH),
)
AUTOSTART = os.getenv("AUTOSTART", "false").lower() == "true"
# Задержка в секундах перед подключением VPN при autostart (1–300)
AUTOSTART_DELAY_SECONDS = parse_autostart_delay_seconds()
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()

# HA ingress proxy IP
INGRESS_ALLOWED_IP = os.getenv("INGRESS_ALLOWED_IP", "172.30.32.2")
ALLOWED_REMOTE = {INGRESS_ALLOWED_IP, "127.0.0.1", "::1"}

VPN_LOCK_PATH = "/tmp/vpn_toggle.lock"
LAST_ACTION_PATH = "/data/last_action.log"

# UI: list protocols (backend currently supports WireGuard only).
PROTOCOLS = [
    {"id": "wireguard", "label": "WireGuard", "enabled": True, "badge": "Stable"},
    {"id": "openvpn", "label": "OpenVPN", "enabled": False, "badge": "Planned"}
]
DEFAULT_PROTOCOL = os.getenv("DEFAULT_PROTOCOL", "wireguard").strip().lower()
