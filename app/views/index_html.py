import os
from html import escape

import config
import protocols


def render_index_html(
    *,
    protocol: str,
    st: dict,
    last: str,
    cfg: str,
    cfg_exists: bool,
    vpn_config_path: str,
) -> str:
    """Build index page HTML from template and context."""
    # Protocol selector options
    options = []
    for p in config.PROTOCOLS:
        sel = "selected" if p["id"] == protocol else ""
        dis = "" if p["enabled"] else "disabled"
        options.append(
            f'<option value="{escape(p["id"])}" {sel} {dis}>'
            f'{escape(p["label"])} — {escape(p["badge"])}</option>'
        )
    options_html = "\n".join(options)

    up = bool(st.get("up"))
    supported = bool(st.get("supported"))
    status_label = "UP" if up else ("DOWN" if supported else "UNSUPPORTED")
    status_class = "ok" if up else ("bad" if supported else "warn")
    supported_badge = "supported" if supported else "not implemented"

    if protocol == "wireguard":
        cfg_badge_class = "ok" if cfg_exists else "bad"
        cfg_badge_text = "present" if cfg_exists else "missing"
        cfg_note = "Saved to " + escape(vpn_config_path)
        cfg_disabled_attr = ""
        save_disabled_attr = ""
        save_hint = "Saving will restart the interface if it is currently UP."
    else:
        cfg_badge_class = "warn"
        cfg_badge_text = "protocol placeholder"
        cfg_note = "Backend for this protocol is not implemented yet."
        cfg_disabled_attr = "disabled"
        save_disabled_attr = "disabled"
        save_hint = "Save/start/stop are disabled until backend is added for this protocol."

    cfg_placeholder = protocols.get_config_placeholder(protocol)
    protocol_esc = escape(protocol)
    cfg_placeholder_esc = escape(cfg_placeholder)
    cfg_esc = escape(cfg)
    ip_inline = escape((st.get("ip") or "").strip() or "—")
    iface_inline = escape(st.get("interface") or "—")
    cfg_path_inline = escape(st.get("config_path") or "—")
    last_content = escape(last.strip() or "(empty)")
    diag_content = escape(
        (st.get("diag") or "").strip()
        or ("(interface down)" if supported else "(not implemented)")
    )
    raw_content = escape(("protocol=" + protocol + "\n" + str(st)).strip())

    path = os.path.join(os.path.dirname(__file__), "..", "templates", "index.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("__OPTIONS_HTML__", options_html)
    html = html.replace("__STATUS_CLASS__", status_class)
    html = html.replace("__SUPPORTED_BADGE__", supported_badge)
    html = html.replace("__STATUS_LABEL__", status_label)
    html = html.replace("__CFG_BADGE_CLASS__", cfg_badge_class)
    html = html.replace("__CFG_BADGE_TEXT__", cfg_badge_text)
    html = html.replace("__CFG_NOTE__", cfg_note)
    html = html.replace("__PROTOCOL_ESC__", protocol_esc)
    html = html.replace("__CFG_PLACEHOLDER_ESC__", cfg_placeholder_esc)
    html = html.replace("__CFG_DISABLED_ATTR__", cfg_disabled_attr)
    html = html.replace("__CFG_ESC__", cfg_esc)
    html = html.replace("__SAVE_DISABLED_ATTR__", save_disabled_attr)
    html = html.replace("__SAVE_HINT__", save_hint)
    html = html.replace("__IP_INLINE__", ip_inline)
    html = html.replace("__IFACE_INLINE__", iface_inline)
    html = html.replace("__CFG_PATH_INLINE__", cfg_path_inline)
    html = html.replace("__LAST_CONTENT__", last_content)
    html = html.replace("__DIAG_CONTENT__", diag_content)
    html = html.replace("__RAW_CONTENT__", raw_content)

    return html
