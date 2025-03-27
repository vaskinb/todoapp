#!/usr/bin/env python
# coding: utf-8
import random

# -----------------------------------------------------------------------------
# --- Typing ---
# -----------------------------------------------------------------------------
from typing import Any, Dict

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
# --- Flask ---
# -----------------------------------------------------------------------------
from flask import Flask, url_for

# -----------------------------------------------------------------------------
# --- Modules ---
# -----------------------------------------------------------------------------
from app.app import create_admin_app
from app.models import db, User
from app.utils.consts import TASK_STATUSES

# -----------------------------------------------------------------------------
# --- Tests ---
# -----------------------------------------------------------------------------
from tests.files.test_credentials import TEST_USERS

# -----------------------------------------------------------------------------
# --- Config ---
# -----------------------------------------------------------------------------
from config import ConfigPath


# -----------------------------------------------------------------------------
#  ______   __     __  __     ______   __  __     ______     ______
# /\  ___\ /\ \   /\_\_\_\   /\__  _\ /\ \/\ \   /\  == \   /\  ___\
# \ \  __\ \ \ \  \/_/\_\/_  \/_/\ \/ \ \ \_\ \  \ \  __<   \ \  __\
#  \ \_\    \ \_\   /\_\/\_\    \ \_\  \ \_____\  \ \_\ \_\  \ \_____\
#   \/_/     \/_/   \/_/\/_/     \/_/   \/_____/   \/_/ /_/   \/_____/
#
# -----------------------------------------------------------------------------
def init_test_users() -> None:
    mf = Field(locale=Locale.EN)

    # -------------------------------------------------------------------------
    # --- Create admin ---
    # -------------------------------------------------------------------------
    admin_user = User(
        email=TEST_USERS['admin']['email'],
        first_name=mf("text.word"),
        last_name=mf("text.word"),
        role='admin',
    )
    admin_user.password = TEST_USERS['admin']['password']
    db.session.add(admin_user)
    db.session.commit()

    # -------------------------------------------------------------------------
    # --- Create user ---
    # -------------------------------------------------------------------------
    new_user = User(
        email=TEST_USERS['user']['email'],
        first_name=mf("text.word"),
        last_name=mf("text.word"),
        role='user',
    )
    new_user.password = TEST_USERS['user']['password']
    db.session.add(new_user)
    db.session.commit()


def init_test_data() -> None:
    init_test_users()


@pytest.fixture(scope="function")
def flask_app(request: Any) -> Flask:
    # ---------------------------------------------------------------------
    # --- Create app ---
    # ---------------------------------------------------------------------
    app = create_admin_app(config_path=ConfigPath.pytest)
    app.config['SERVER_NAME'] = 'localhost.localdomain'

    app.db = db
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()

        # ---------------------------------------------------------------------
        # --- Init test data ---
        # ---------------------------------------------------------------------
        init_test_data()

        yield app

        db.session.remove()
        db.drop_all()

    return app


@pytest.fixture(scope="function")
def client(flask_app: Flask) -> Any:
    flask_app.config['TESTING'] = True
    flask_app.config['PROPAGATE_EXCEPTIONS'] = False

    with flask_app.test_client() as client:
        client.raise_on_exception = False
        yield client


@pytest.fixture(scope="function")
def authenticated_admin_user(client: Flask) -> Flask:
    client.post(
        url_for('auth.login'),
        data={
            'email': 'admin@gmail.com',
            'password': 'admin@gmail.com',
            'remember_me': 'true'
        },
        follow_redirects=True,
    )
    return client


@pytest.fixture(scope="function")
def authenticated_user(client: Flask) -> Flask:
    client.post(
        url_for('auth.login'), follow_redirects=True,
        data={
            'email': 'user@gmail.com',
            'password': 'user@gmail.com',
            'remember_me': 'true'
        }
    )
    return client


@pytest.fixture
def sample_task_data() -> Dict:
    mf = Field(locale=Locale.EN)
    return {
        "title": mf("text.title"),
        "description": mf("text.sentence"),
        "status": random.choice(TASK_STATUSES),
        "due_date": mf('datetime.date').strftime('%Y-%m-%d'),
    }
