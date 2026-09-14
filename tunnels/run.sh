#!/usr/bin/with-contenv bashio
set -euo pipefail

CONFIG_PATH=/data/options.json

# Universal names (must match config.py INTERFACE_NAME and CONFIG_FILENAME)
VPN_INTERFACE="tunnels0"
CONFIG_FILE="tunnels.conf"
# Protocol-agnostic runtime dir (avoids /etc/wireguard when adding OpenVPN etc.)
VPN_RUNTIME_DIR="/etc/tunnels"
AUTOSTART="$(bashio::config 'autostart')"
AUTOSTART_DELAY_SECONDS="$(bashio::config 'autostart_delay_seconds')"
AUTOSTART_DELAY_SECONDS="${AUTOSTART_DELAY_SECONDS:-5}"
LOG_LEVEL="$(bashio::config 'log_level')"
INGRESS_ALLOWED_IP="$(bashio::config 'ingress_allow_ip')"
DEFAULT_PROTOCOL="$(bashio::config 'default_protocol')"
DEFAULT_PROTOCOL="${DEFAULT_PROTOCOL:-wireguard}"

SRC="/config/${CONFIG_FILE}"
DST="${VPN_RUNTIME_DIR}/${VPN_INTERFACE}.conf"

mkdir -p "${VPN_RUNTIME_DIR}"

if [ -f "${SRC}" ]; then
  cp "${SRC}" "${DST}"
  chmod 600 "${DST}"
  bashio::log.info "VPN config loaded: ${SRC} -> ${DST}"
else
  bashio::log.warning "WireGuard config file not found: ${SRC}"
fi

AWG_SRC="/config/tunnels-amneziawg.conf"
AWG_DST="${VPN_RUNTIME_DIR}/${VPN_INTERFACE}-amneziawg.conf"
if [ -f "${AWG_SRC}" ]; then
  cp "${AWG_SRC}" "${AWG_DST}"
  chmod 600 "${AWG_DST}"
  bashio::log.info "AmneziaWG config loaded: ${AWG_SRC} -> ${AWG_DST}"
fi

export VPN_INTERFACE
export VPN_CONFIG_DST="${DST}"
export VPN_CONFIG_SRC="${SRC}"
export AUTOSTART
export AUTOSTART_DELAY_SECONDS
export LOG_LEVEL
export INGRESS_ALLOWED_IP
export DEFAULT_PROTOCOL

exec python3 -u /app/server.py
