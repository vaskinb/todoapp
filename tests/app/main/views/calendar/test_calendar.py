#!/usr/bin/env python
# coding: utf-8
# -----------------------------------------------------------------------------
# --- Typing ---
# -----------------------------------------------------------------------------
from typing import Any

# -----------------------------------------------------------------------------
# --- Flask ---
# -----------------------------------------------------------------------------
from flask import url_for

# -----------------------------------------------------------------------------
# --- HTTP status ---
# -----------------------------------------------------------------------------
from http import HTTPStatus

# -----------------------------------------------------------------------------
# --- Pytest ---
# -----------------------------------------------------------------------------
import pytest

# -----------------------------------------------------------------------------
# --- Mimesis ---
# -----------------------------------------------------------------------------
from mimesis import Field, Generic
from mimesis.locales import Locale


# -----------------------------------------------------------------------------
#  ______   ______     ______     ______   ______
# /\__  _\ /\  ___\   /\  ___\   /\__  _\ /\  ___\
# \/_/\ \/ \ \  __\   \ \___  \  \/_/\ \/ \ \___  \
#    \ \_\  \ \_____\  \/\_____\    \ \_\  \/\_____\
#     \/_/   \/_____/   \/_____/     \/_/   \/_____/
#
# -----------------------------------------------------------------------------
@pytest.mark.usefixtures("authenticated_admin_user")
def test_calendar_admin_get(client: Any) -> None:
    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    response = client.get(url_for('calendar.main'))

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert response.status_code == HTTPStatus.OK


def test_calendar_no_authorize_get(client: Any) -> None:
    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    response = client.get(url_for('calendar.main'))

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert response.status_code == HTTPStatus.FOUND
    assert response.location.startswith(url_for('auth.login', _external=True))


@pytest.mark.usefixtures("authenticated_user")
def test_calendar_user_get(client: Any) -> None:
    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    response = client.get(url_for('calendar.main'))

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert response.status_code == HTTPStatus.OK
