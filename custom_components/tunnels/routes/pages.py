from html import escape

from flask import Blueprint, request, abort, redirect, Response

import config
import config_store
import protocols
import utils
import vpn_control
from views.index_html import render_index_html

pages_bp = Blueprint("pages", __name__)


@pages_bp.get("/")
def index():
    protocol = protocols.get_protocol_from_request()
    st = protocols.proto_status(protocol)

    last = utils.read_last_action()
    cfg = config_store.read_config() if protocol == "wireguard" else ""
    cfg_exists = bool(cfg.strip()) if protocol == "wireguard" else False

    html = render_index_html(
        protocol=protocol,
        st=st,
        last=last,
        cfg=cfg,
        cfg_exists=cfg_exists,
        vpn_config_path=config.VPN_CONFIG_PATH,
    )
    return Response(html, mimetype="text/html")


@pages_bp.post("/config")
def save_config():
    protocol = protocols.get_protocol_from_request()
    if protocol != "wireguard":
        abort(400, f"Protocol not implemented: {protocol}")

    cfg = request.form.get("config", "").strip()
    if not cfg:
        abort(400, "Empty config")

    ok, msg = config_store.write_config(cfg)
    utils.write_last_action("save_config", ok, msg)

    if ok and vpn_control.vpn_is_up():
        vpn_control.vpn_down()
        vpn_control.vpn_up()

    return redirect(f"./?protocol={escape(protocol)}", code=303)


@pages_bp.post("/start")
def start():
    protocol = protocols.get_protocol_from_request()
    if protocol != "wireguard":
        abort(400, f"Protocol not implemented: {protocol}")

    ok, out = vpn_control.vpn_up()
    utils.write_last_action("start", ok, out)
    return redirect(f"./?protocol={escape(protocol)}", code=303)


@pages_bp.post("/stop")
def stop():
    protocol = protocols.get_protocol_from_request()
    if protocol != "wireguard":
        abort(400, f"Protocol not implemented: {protocol}")

    ok, out = vpn_control.vpn_down()
    utils.write_last_action("stop", ok, out)
    return redirect(f"./?protocol={escape(protocol)}", code=303)
