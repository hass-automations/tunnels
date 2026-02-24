# Protocol-agnostic path (must match run.sh DST / config.py VPN_RUNTIME_DIR)
wg-quick down /etc/tunnels/tunnels0.conf 2>/dev/null || true
pidof openvpn >/dev/null && kill $(pidof openvpn) 2>/dev/null || true
