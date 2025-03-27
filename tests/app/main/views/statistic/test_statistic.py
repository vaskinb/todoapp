#!/usr/bin/env python
# coding: utf-8
import datetime

# -----------------------------------------------------------------------------
# --- Typing ---
# -----------------------------------------------------------------------------
from typing import Any, List

# -----------------------------------------------------------------------------
# --- Flask ---
# -----------------------------------------------------------------------------
from flask import url_for, Flask

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
# --- Models ---
# -----------------------------------------------------------------------------
from app import models

# -----------------------------------------------------------------------------
# --- Module ---
# -----------------------------------------------------------------------------
from app.main.views.statistic.statistic import (
    count_tasks, get_daily_stats, get_weekly_stats, get_tasks_statistics,
)


# -----------------------------------------------------------------------------
#  ______   __     __  __     ______   __  __     ______     ______
# /\  ___\ /\ \   /\_\_\_\   /\__  _\ /\ \/\ \   /\  == \   /\  ___\
# \ \  __\ \ \ \  \/_/\_\/_  \/_/\ \/ \ \ \_\ \  \ \  __<   \ \  __\
#  \ \_\    \ \_\   /\_\/\_\    \ \_\  \ \_____\  \ \_\ \_\  \ \_____\
#   \/_/     \/_/   \/_/\/_/     \/_/   \/_____/   \/_/ /_/   \/_____/
#
# -----------------------------------------------------------------------------
@pytest.fixture
def create_sample_tasks(flask_app: Flask) -> List[models.Task]:
    field = Field(locale=Locale.EN)
    test_user_id = 2
    date = datetime.date.today()

    tasks_data = [
        {"status": "pending"},
        {"status": "active"},
        {"status": "completed"},
        {"status": "completed"},
    ]
    tasks = []
    for data in tasks_data:
        task = models.Task(
            user_id=test_user_id,
            title=field("text.title"),
            description=field("text.sentence"),
            status=data["status"],
            due_date=date,
        )
        tasks.append(task)
    models.db.session.add_all(tasks)
    models.db.session.commit()

    return tasks


# -----------------------------------------------------------------------------
#  ______   ______     ______     ______   ______
# /\__  _\ /\  ___\   /\  ___\   /\__  _\ /\  ___\
# \/_/\ \/ \ \  __\   \ \___  \  \/_/\ \/ \ \___  \
#    \ \_\  \ \_____\  \/\_____\    \ \_\  \/\_____\
#     \/_/   \/_____/   \/_____/     \/_/   \/_____/
#
# -----------------------------------------------------------------------------
def test_count_tasks(flask_app: Flask, create_sample_tasks: List) -> None:
    # -------------------------------------------------------------------------
    # --- Arrange ---
    # --------------------------------------------------------------------------
    test_user_id = 2

    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    counts = count_tasks(test_user_id)

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert counts['total'] == 4
    assert counts['pending'] == 1
    assert counts['active'] == 1
    assert counts['completed'] == 2


def test_get_daily_stats(flask_app: Flask, create_sample_tasks: List) -> None:
    # -------------------------------------------------------------------------
    # --- Arrange ---
    # -------------------------------------------------------------------------
    test_user_id = 2
    start_day = datetime.date.today() - datetime.timedelta(days=6)

    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    daily_stats = get_daily_stats(test_user_id, start_day)

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert len(daily_stats) == 7
    for data in daily_stats.values():
        assert 'total' in data
        assert 'completed' in data


def test_get_weekly_stats(flask_app: Flask, create_sample_tasks: List) -> None:
    # -------------------------------------------------------------------------
    # --- Arrange ---
    # -------------------------------------------------------------------------
    user = models.User.query.filter_by(email='user@gmail.com').first()
    today = datetime.date.today()
    start_week = today - datetime.timedelta(weeks=3, days=today.weekday())

    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    weekly_stats = get_weekly_stats(user.id, start_week)

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert len(weekly_stats) == 4
    for data in weekly_stats.values():
        assert 'total' in data
        assert 'completed' in data


def test_get_tasks_statistics(
        flask_app: Flask, create_sample_tasks: List
) -> None:
    # -------------------------------------------------------------------------
    # --- Arrange ---
    # -------------------------------------------------------------------------
    user = models.User.query.filter_by(email='user@gmail.com').first()

    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    stats = get_tasks_statistics(user.id)

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert 'counts' in stats
    assert 'daily' in stats
    assert 'weekly' in stats

    assert isinstance(stats['daily']['labels'], list)
    assert isinstance(stats['daily']['total'], list)
    assert isinstance(stats['daily']['completed'], list)
    assert isinstance(stats['weekly']['labels'], list)
    assert isinstance(stats['weekly']['total'], list)
    assert isinstance(stats['weekly']['completed'], list)


@pytest.mark.usefixtures("authenticated_user")
def test_statistic_route_authenticated(client: Any) -> None:
    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    response = client.get(url_for('statistic.main'))

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert response.status_code == HTTPStatus.OK
    assert b"statistic" in response.data.lower()


def test_statistic_route_unauthenticated(client: Any) -> None:
    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    response = client.get(url_for('statistic.main'))

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert response.status_code in (HTTPStatus.FOUND, HTTPStatus.SEE_OTHER)
    assert response.location.startswith(url_for('auth.login', _external=True))
