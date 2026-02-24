import os

from utils import parse_autostart_delay_seconds

# Protocol-agnostic VPN settings (WireGuard when DEFAULT_PROTOCOL=wireguard).
# Universal interface name for this add-on (must match run.sh VPN_INTERFACE).
INTERFACE_NAME = "tunnels0"
VPN_INTERFACE = os.getenv("VPN_INTERFACE", INTERFACE_NAME)
# Universal VPN config filename in add-on config folder (must match run.sh CONFIG_FILE).
CONFIG_FILENAME = "tunnels.conf"
# Protocol-agnostic runtime dir (same for WireGuard, OpenVPN, etc.; must match run.sh VPN_RUNTIME_DIR).
VPN_RUNTIME_DIR = "/etc/tunnels"
# Runtime path to VPN config (inside container); binary (wg-quick, openvpn) gets this path.
VPN_CONFIG_PATH = os.getenv(
    "VPN_CONFIG_PATH",
    os.getenv("VPN_CONFIG_DST", f"{VPN_RUNTIME_DIR}/{VPN_INTERFACE}.conf"),
)
# Persistent path (addon_config, survives restart)
VPN_CONFIG_PERSISTENT = os.getenv(
    "VPN_CONFIG_SRC",
    os.getenv("VPN_CONFIG_PERSISTENT", f"/config/{CONFIG_FILENAME}"),
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
