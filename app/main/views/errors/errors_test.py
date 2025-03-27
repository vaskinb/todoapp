#!/usr/bin/env python
# coding: utf-8
# -----------------------------------------------------------------------------
# --- Flask ---
# -----------------------------------------------------------------------------
from flask import Blueprint, abort

# -----------------------------------------------------------------------------
# --- Errors ---
# -----------------------------------------------------------------------------
from app.main.views.errors import errors

# -----------------------------------------------------------------------------
# --- Blueprint ---
# -----------------------------------------------------------------------------
test_errors_bp = Blueprint("test_errors", __name__)


@test_errors_bp.route("/test-403")
def test_403():
    abort(403)


@test_errors_bp.route("/test-500")
def test_500():
    abort(500)


@test_errors_bp.route("/test-exception")
def test_exception():
    raise Exception("Test exception")
