#!/usr/bin/env python
# coding: utf-8
# -----------------------------------------------------------------------------
# --- App settings ---
# -----------------------------------------------------------------------------
from app.app import create_admin_app

# -----------------------------------------------------------------------------
# --- Config---
# -----------------------------------------------------------------------------
from config import ConfigPath

# -----------------------------------------------------------------------------
app = create_admin_app(config_path=ConfigPath.production)

if __name__ == "__main__":
    app.run(
        use_debugger=app.config["DEBUG"],
        host=app.config["IP_ADDRESS"],
        port=app.config["ADMIN_PORT"]
    )
