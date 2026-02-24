# Changelog

## 0.2.0

- API: extended status with `last_handshake_iso`, `last_handshake_seconds_ago`, `transfer_rx`, `transfer_tx`, `endpoint` for automations
- UI: form submit via fetch so buttons no longer redirect to HA root (Ingress-safe)
- Optional Home Assistant integration: add `integration/` to `custom_components/tunnels` for sensors (VPN connected, protocol, last handshake, IP, transfer, endpoint)
- Config: explicit `icon: icon.png`; `image` commented out by default for local install

## 0.1.0

- Initial release
- WireGuard: start/stop, config edit, diagnostics, autostart
- Ingress-only UI
- Protocol-agnostic paths (/etc/tunnels), universal names (tunnels0, tunnels.conf)
