# Changelog

## 0.3.8

- Fix: inject `Table = off` + manual PostUp/PostDown routing when `AllowedIPs = 0.0.0.0/0` — avoids `sysctl src_valid_mark` which is read-only on HA OS regardless of `SYS_ADMIN` capability
- The VPN server IP gets a host route via the original gateway (prevents routing loop); default is routed through the VPN interface (metric 0, highest priority)

## 0.3.7

- Fix: add `SYS_ADMIN` capability — required for `sysctl net.ipv4.conf.all.src_valid_mark=1` when routing all traffic through VPN (`AllowedIPs = 0.0.0.0/0`)

## 0.3.6

- Fix: IPv6 `AllowedIPs` (`::/0`) stripped at runtime — `ip6_tables` module absent in HA containers causes `awg-quick` to roll back the whole connection

## 0.3.5

- Fix: AmneziaWG config range values (e.g. `PersistentKeepalive = 25-35`) are resolved to midpoint integers before passing to `awg setconf` — eliminates "Configuration parsing error"
- Fix: stale `amneziawg-go` process (left from a failed previous start) is killed before each new start — eliminates "TUN not pollable" error on retry
- Fix: protocol tab on first page load now navigates to the correct server-rendered page (previously localStorage could restore the wrong tab without refreshing the config)

## 0.3.4

- Fix: runtime config is always `tunnels0.conf` (wg-quick/awg-quick require filename == interface name); `vpn_up()` copies the correct persistent config there before each start

## 0.3.3

- Fix: auto-migrate `tunnels.conf` → `tunnels-amneziawg.conf` at startup if it contains AmneziaWG params (Jc/H1/S1 etc.) — WireGuard tab no longer shows leftover AmneziaWG config

## 0.3.2

- Fix: WireGuard and AmneziaWG now use separate config files (`tunnels.conf` vs `tunnels-amneziawg.conf`) — switching protocol tabs no longer overwrites each other's config

## 0.3.1

- Fix: Python 3.9 compatibility (`dict | None` syntax replaced with `from __future__ import annotations`)
- Fix: Docker builder now includes `bash` so `awg-quick` gets installed by `make install`
- Fix: multi-stage build uses `golang:1.25-alpine` to satisfy `amneziawg-go` Go version requirement

## 0.3.0

- AmneziaWG: added as a second protocol option (Beta); builds `amneziawg-go` and `awg`/`awg-quick` from source at image build time
- Fix: `vpn_up()` now detects config changes via sha256 hash and restarts the interface automatically — no more manual Stop→Start after editing config
- New: `handshake_age_s` field in status API — seconds since the last peer handshake (null if no handshake yet)
- Config: added `default_protocol` option (`wireguard` | `amneziawg`)
- Config: added `/dev/net/tun` device (required for AmneziaWG userspace mode)

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
