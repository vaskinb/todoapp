#!/usr/bin/env python
# coding: utf-8
import os
import sys

# -----------------------------------------------------------------------------
# --- Logger ---
# -----------------------------------------------------------------------------
from loguru import logger

# -----------------------------------------------------------------------------
# --- Migrations ---
# -----------------------------------------------------------------------------
from flask_migrate import Migrate

# -----------------------------------------------------------------------------
# --- App settings ---
# -----------------------------------------------------------------------------
from app.app import create_admin_app

# -----------------------------------------------------------------------------
# --- Models---
# -----------------------------------------------------------------------------
from app.models import db

# -----------------------------------------------------------------------------
# --- Config ---
# -----------------------------------------------------------------------------
from config import ConfigPath

# -----------------------------------------------------------------------------
# --- Set config ---
# -----------------------------------------------------------------------------
prod_conf = ConfigPath.production
dev_conf = ConfigPath.development
test_conf = ConfigPath.pytest
docker_conf = ConfigPath.docker


# -----------------------------------------------------------------------------
# --- Mode detection ---
# -----------------------------------------------------------------------------
is_docker = os.environ.get("IS_DOCKER") == "1"
application_mode = str(sys.argv[1])

# -----------------------------------------------------------------------------
# --- Config path resolution ---
# -----------------------------------------------------------------------------
if is_docker:
    config_path = docker_conf
elif application_mode in ["tests", "coverage"]:
    config_path = test_conf
else:
    config_path = prod_conf if os.path.isfile(prod_conf) else dev_conf

# -----------------------------------------------------------------------------
# --- Create app ---
# -----------------------------------------------------------------------------
app = create_admin_app(config_path=config_path)
migrate = Migrate(app, db, compare_type=True)

# -----------------------------------------------------------------------------
match application_mode:
    case "admin":
        app.run(
            use_debugger=app.config["DEBUG"],
            use_reloader=True,
            host=app.config["IP_ADDRESS"],
            port=app.config["ADMIN_PORT"]
        )

    case _:
        pass
