# Home Assistant Add-on: Tunnels

Tunnels: VPN client manager for remote access to Home Assistant.

## About

This add-on lets you run a VPN client (WireGuard) on your Home Assistant host so you can reach your smart home securely from outside your local network. Use the built-in Ingress UI to start and stop the tunnel, edit the VPN config, and view status and diagnostics.

**Typical use case:**

- **At home** — Use your LAN (Wi‑Fi); no VPN. Home Assistant is available at your internal URL (e.g. `http://192.168.1.x:8123`).
- **Away from home** — Turn on the VPN (e.g. WireGuard on your phone) and connect to Home Assistant over the VPN (e.g. `http://10.99.0.2:8123`). The add-on runs the WireGuard client on the HA host so the host is reachable inside the VPN.

The add-on uses **host network** and **NET_ADMIN** so the WireGuard interface runs in the host’s network namespace. The UI is only available via **Ingress** (no direct access to the add-on port from LAN).

Supported today:

- **WireGuard** — Full support: start/stop, config edit, diagnostics.

Planned (UI placeholders only for now):

- OpenVPN

## Configuration

Add-on options (from the add-on **Configuration** tab):

| Option            | Type    | Default        | Description                                      |
|-------------------|--------|----------------|--------------------------------------------------|
| `interface`       | string | `wg0`          | WireGuard interface name                         |
| `config_file`     | string | `wg0.conf`     | Config file name in the add-on config directory  |
| `autostart`       | bool   | `false`        | Bring the VPN up automatically when the add-on starts |
| `ingress_allow_ip`| string | `172.30.32.2`  | IP allowed to reach the app (Ingress proxy)      |
| `log_level`       | list   | `info`         | Log level: `debug`, `info`, `warning`, `error`    |

### Where the WireGuard config lives

- **On the host:** Put your WireGuard client config in the add-on config folder, named as in `config_file` (e.g. `wg0.conf`).  
  Path is typically: `/addon_configs/<addon_uuid>/wg0.conf` (see **Settings → Add-ons → Tunnels → Info** and your file editor/SSH to find the exact folder).

- **Inside the container:** That file is mounted at `/config/wg0.conf` and at add-on start is copied to `/etc/wireguard/wg0.conf`. The Ingress UI can also **edit and save** the config; saved content is written to `/etc/wireguard/wg0.conf`. After changing the file on disk, restart the add-on so the copy step runs again.

### Example WireGuard client config (`wg0.conf`)

```ini
[Interface]
PrivateKey = <YOUR_PRIVATE_KEY>
Address = 10.99.0.2/32

[Peer]
PublicKey = <SERVER_PUBLIC_KEY>
Endpoint = <VPS_IP>:51820
AllowedIPs = 10.99.0.0/24
PersistentKeepalive = 25
```

Use a VPN subnet that does not conflict with your LAN. For full setup of the WireGuard server (e.g. on a VPS) and keys, see **DOCS.md** in this repository.

## Security

- The add-on UI is intended to be used **only via Ingress**. Requests from other IPs (e.g. direct access to port 8099 from LAN) are rejected with 403.
- The add-on runs with `host_network: true` and `NET_ADMIN` so it can manage the WireGuard interface on the host.

