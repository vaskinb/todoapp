#!/usr/bin/env python
# coding: utf-8
# -----------------------------------------------------------------------------
# --- Typing ---
# -----------------------------------------------------------------------------
from typing import Union

# -----------------------------------------------------------------------------
# --- Flask ---
# -----------------------------------------------------------------------------
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_principal import Principal, Identity

# -----------------------------------------------------------------------------
# --- Models ---
# -----------------------------------------------------------------------------
from app.models import User

# -----------------------------------------------------------------------------
# --- Blueprints ---
# -----------------------------------------------------------------------------
from app.auth.views import auth as auth_blueprint
from app.main.views.dashboard.main import main_bp
from app.main.views.calendar.calendar import calendar_bp
from app.main.views.statistic.statistic import statistic_bp

# -----------------------------------------------------------------------------
# --- Config ---
# -----------------------------------------------------------------------------
from config import Config


def create_admin_app(config_path: str = "conf/development.conf") -> Flask:
    app = Flask(__name__)

    # -------------------------------------------------------------------------
    # --- Init config ---
    # -------------------------------------------------------------------------
    Config(app, config_path)

    # -------------------------------------------------------------------------
    # --- Login manager ---
    # -------------------------------------------------------------------------
    login_manager = LoginManager()
    login_manager.session_protection = 'basic'
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id) -> User:
        return User.query.get(int(user_id))

    login_manager.init_app(app)

    # -------------------------------------------------------------------------
    # --- Principal init ---
    # -------------------------------------------------------------------------
    principal = Principal(app)

    @principal.identity_loader
    def load_identity_when_session_expires() -> Union[None, Identity]:
        if hasattr(current_user, 'id'):
            return Identity(current_user.id)
        return None

    # -------------------------------------------------------------------------
    # --- DB access ---
    # -------------------------------------------------------------------------
    database = SQLAlchemy()
    database.init_app(app)

    # -------------------------------------------------------------------------
    # --- Register blueprints for routing ---
    # -------------------------------------------------------------------------
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(statistic_bp)

    # -------------------------------------------------------------------------
    # --- Register blueprints for tests ---
    # -------------------------------------------------------------------------
    if app.config.get("TESTING"):
        from app.main.views.errors.errors_test import test_errors_bp
        app.register_blueprint(test_errors_bp)

    return app
