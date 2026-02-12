#!/usr/bin/with-contenv bashio
set -euo pipefail

CONFIG_PATH=/data/options.json

WG_INTERFACE="$(bashio::config 'interface')"
WG_CONFIG_FILE="$(bashio::config 'config_file')"
AUTOSTART="$(bashio::config 'autostart')"
AUTOSTART_DELAY_SECONDS="$(bashio::config 'autostart_delay_seconds')"
AUTOSTART_DELAY_SECONDS="${AUTOSTART_DELAY_SECONDS:-5}"
LOG_LEVEL="$(bashio::config 'log_level')"
INGRESS_ALLOWED_IP="$(bashio::config 'ingress_allow_ip')"

SRC="/config/${WG_CONFIG_FILE}"
DST="/etc/wireguard/${WG_INTERFACE}.conf"

mkdir -p /etc/wireguard

if [ -f "${SRC}" ]; then
  cp "${SRC}" "${DST}"
  chmod 600 "${DST}"
  bashio::log.info "WireGuard config loaded: ${SRC} -> ${DST}"
else
  bashio::log.warning "WireGuard config file not found: ${SRC}"
  bashio::log.warning "Upload config in the add-on UI or put ${WG_CONFIG_FILE} into the add-on config folder."
fi

export WG_INTERFACE
export WG_CONFIG_DST="${DST}"
export WG_CONFIG_SRC="${SRC}"
export AUTOSTART
export AUTOSTART_DELAY_SECONDS
export LOG_LEVEL
export INGRESS_ALLOWED_IP

exec python3 -u /app/server.py
