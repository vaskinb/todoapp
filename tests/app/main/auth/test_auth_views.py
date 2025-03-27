#!/usr/bin/env python
# coding: utf-8
import random

# -----------------------------------------------------------------------------
# --- Typing ---
# -----------------------------------------------------------------------------
from typing import Any, Dict

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
from mimesis import Field, Generic, Person
from mimesis.locales import Locale

# -----------------------------------------------------------------------------
# --- Models ---
# -----------------------------------------------------------------------------
from app.models import db, User


# -----------------------------------------------------------------------------
#  ______   __     __  __     ______   __  __     ______     ______
# /\  ___\ /\ \   /\_\_\_\   /\__  _\ /\ \/\ \   /\  == \   /\  ___\
# \ \  __\ \ \ \  \/_/\_\/_  \/_/\ \/ \ \ \_\ \  \ \  __<   \ \  __\
#  \ \_\    \ \_\   /\_\/\_\    \ \_\  \ \_____\  \ \_\ \_\  \ \_____\
#   \/_/     \/_/   \/_/\/_/     \/_/   \/_____/   \/_/ /_/   \/_____/
#
# -----------------------------------------------------------------------------
@pytest.fixture
def sample_signup_data() -> Dict:
    mf = Field(locale=Locale.EN)
    person = Person(locale=Locale.EN)
    password = person.password(length=random.randint(6, 20))

    return {
        "email": mf("person.email"),
        "password": password,
        "confirm_password": password,
        "first_name": mf("person.first_name"),
        "last_name": mf("person.last_name"),
    }


# -----------------------------------------------------------------------------
#  ______   ______     ______     ______   ______
# /\__  _\ /\  ___\   /\  ___\   /\__  _\ /\  ___\
# \/_/\ \/ \ \  __\   \ \___  \  \/_/\ \/ \ \___  \
#    \ \_\  \ \_____\  \/\_____\    \ \_\  \/\_____\
#     \/_/   \/_____/   \/_____/     \/_/   \/_____/
#
# -----------------------------------------------------------------------------
def test_login_success(client) -> None:
    # -------------------------------------------------------------------------
    # --- Arrange ---
    # -------------------------------------------------------------------------
    login_data = {
        "email": "user@gmail.com",
        "password": "user@gmail.com",
        "remember_me": "true"
    }

    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    response = client.post(
        url_for("auth.login"), data=login_data, follow_redirects=False
    )

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert response.status_code in (HTTPStatus.FOUND, HTTPStatus.SEE_OTHER)
    assert response.headers["Location"].endswith(url_for("main.index"))


def test_login_failure(client) -> None:
    # -------------------------------------------------------------------------
    # --- Arrange ---
    # -------------------------------------------------------------------------
    login_data = {
        "email": "user@gmail.com",
        "password": "wrongpassword",
        "remember_me": True,
    }

    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    response = client.post(
        url_for("auth.login"), data=login_data, follow_redirects=True
    )
    response_data = response.get_data(as_text=True)

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert response.status_code == HTTPStatus.OK
    assert "Email or password are wrong" in response_data


def test_signup_success(client: Any, sample_signup_data: Dict) -> None:
    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    response = client.post(
        url_for("auth.signup"), data=sample_signup_data, follow_redirects=True
    )

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert response.status_code == 200
    assert "Dashboard" in response.get_data(as_text=True)


def test_signup_existing(client: Any, sample_signup_data: Dict) -> None:
    # -------------------------------------------------------------------------
    # --- Arrange ---
    # -------------------------------------------------------------------------
    existing_user = User(
        email=sample_signup_data["email"],
        first_name=sample_signup_data["first_name"],
        last_name=sample_signup_data["last_name"],
        role='user',
    )
    existing_user.password = sample_signup_data["password"]
    db.session.add(existing_user)
    db.session.commit()

    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    response = client.post(
        url_for("auth.signup"), data=sample_signup_data, follow_redirects=True
    )

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert response.status_code == 200
    assert "Email is already registered" in response.get_data(as_text=True)


@pytest.mark.usefixtures("authenticated_user")
def test_logout(client: Any) -> None:
    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    response = client.get(url_for("auth.logout"), follow_redirects=False)

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert response.status_code in (HTTPStatus.FOUND, HTTPStatus.SEE_OTHER)
    assert response.headers["Location"].endswith(url_for("auth.login"))
