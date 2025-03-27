#!/usr/bin/env python
# coding: utf-8
# -----------------------------------------------------------------------------
# --- Flask ---
# -----------------------------------------------------------------------------
from flask import render_template

# -----------------------------------------------------------------------------
# --- Logger ---
# -----------------------------------------------------------------------------
from loguru import logger

# -----------------------------------------------------------------------------
# --- Blueprint ---
# -----------------------------------------------------------------------------
from app.main.views import main_bp


# -----------------------------------------------------------------------------
#  ______     ______     ______     ______     ______     ______
# /\  ___\   /\  == \   /\  == \   /\  __ \   /\  == \   /\  ___\
# \ \  __\   \ \  __<   \ \  __<   \ \ \/\ \  \ \  __<   \ \___  \
#  \ \_____\  \ \_\ \_\  \ \_\ \_\  \ \_____\  \ \_\ \_\  \/\_____\
#   \/_____/   \/_/ /_/   \/_/ /_/   \/_____/   \/_/ /_/   \/_____/
#
# -----------------------------------------------------------------------------
@main_bp.app_errorhandler(403)
def page_403(error):
    logger.error(error)
    return render_template('errors/403.html'), 403


@main_bp.app_errorhandler(404)
def page_404(error):
    logger.error(error)
    return render_template('errors/404.html'), 404


@main_bp.app_errorhandler(500)
def page_500(error):
    logger.error(error)
    return render_template('errors/500.html'), 500


@main_bp.app_errorhandler(Exception)
def handle_exception(error):
    logger.error(error)
    return render_template('errors/500.html'), 500
