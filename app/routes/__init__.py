from flask import request, abort

import config


def register_routes(app):
    """Register blueprints and before_request hook."""
    from .pages import pages_bp
    from .api import api_bp

    app.before_request(_restrict_ingress_only)
    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp)


def _restrict_ingress_only():
    if request.remote_addr not in config.ALLOWED_REMOTE:
        abort(403)
