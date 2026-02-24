from flask import Blueprint, request, jsonify

import config
import protocols

api_bp = Blueprint("api", __name__)


@api_bp.get("/api/status")
def api_status():
    protocol = (request.args.get("protocol") or config.DEFAULT_PROTOCOL).strip().lower()
    if not any(x["id"] == protocol for x in config.PROTOCOLS):
        protocol = "wireguard"
    return jsonify(protocols.proto_status(protocol))


@api_bp.get("/health")
def health():
    return "ok"
