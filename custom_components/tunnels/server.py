import time

from flask import Flask

import config
import routes
import utils
import vpn_control


def create_app() -> Flask:
    app = Flask(__name__)
    routes.register_routes(app)
    return app


def main() -> None:
    if config.AUTOSTART:
        # Задержка перед подключением VPN (сеть контейнера успевает подняться)
        time.sleep(config.AUTOSTART_DELAY_SECONDS)
        ok, out = vpn_control.vpn_up()
        utils.write_last_action("autostart", ok, out)

    app = create_app()
    app.run(host="0.0.0.0", port=8099, debug=False)


if __name__ == "__main__":
    main()
