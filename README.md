# Tunnels – Home Assistant add-on repository

This repository contains add-ons for VPN-based remote access to Home Assistant.

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fhass-automations%2Ftunnels)

## Add-ons

### [Tunnels](./tunnels)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

_VPN client (WireGuard) on the HA host for secure remote access. Start/stop, edit config, diagnostics via Ingress UI._

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg

## Local / development

- **What to add in HA:** the **repository root** (the folder that contains `repository.yaml` and the `tunnels/` subfolder). Do **not** add only the `tunnels/` folder — Supervisor needs `repository.yaml` at the root to see the repo.
- **Icon:** the add-on icon is `tunnels/icon.png`. If the icon does not show, ensure you added the repo root URL/path so that Supervisor can load `tunnels/icon.png`.
- **Avoid `tunnels/tunnels` on disk:** if you clone into a folder also named `tunnels`, you get `tunnels/tunnels/` (repo folder / addon folder). Clone into another name instead (e.g. `tunnels-repo` or `ha-tunnels`) so you have e.g. `tunnels-repo/tunnels/` and no confusion.
