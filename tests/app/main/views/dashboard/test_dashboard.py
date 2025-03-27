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
from mimesis import Field, Generic
from mimesis.locales import Locale

# -----------------------------------------------------------------------------
# --- Models ---
# -----------------------------------------------------------------------------
from app import models
from app.utils.consts import TASK_STATUSES


# -----------------------------------------------------------------------------
#  ______   __     __  __     ______   __  __     ______     ______
# /\  ___\ /\ \   /\_\_\_\   /\__  _\ /\ \/\ \   /\  == \   /\  ___\
# \ \  __\ \ \ \  \/_/\_\/_  \/_/\ \/ \ \ \_\ \  \ \  __<   \ \  __\
#  \ \_\    \ \_\   /\_\/\_\    \ \_\  \ \_____\  \ \_\ \_\  \ \_____\
#   \/_/     \/_/   \/_/\/_/     \/_/   \/_____/   \/_/ /_/   \/_____/
#
# -----------------------------------------------------------------------------
@pytest.fixture
def updated_task_data() -> Dict:
    mf = Field(locale=Locale.EN)
    return {
        "title": mf("text.title"),
        "description": mf("text.sentence"),
        "status": random.choice(TASK_STATUSES),
        "due_date": mf("datetime.date").strftime("%Y-%m-%d"),
    }


@pytest.fixture
def sample_other_user_task(sample_task_data: Dict) -> models.Task:
    other_user_id = 1
    task = models.Task(
        title=sample_task_data["title"],
        description=sample_task_data["description"],
        status=sample_task_data["status"],
        due_date=sample_task_data["due_date"],
        user_id=other_user_id,
    )
    models.db.session.add(task)
    models.db.session.commit()

    return task


# -----------------------------------------------------------------------------
#  ______   ______     ______     ______   ______
# /\__  _\ /\  ___\   /\  ___\   /\__  _\ /\  ___\
# \/_/\ \/ \ \  __\   \ \___  \  \/_/\ \/ \ \___  \
#    \ \_\  \ \_____\  \/\_____\    \ \_\  \/\_____\
#     \/_/   \/_____/   \/_____/     \/_/   \/_____/
#
# -----------------------------------------------------------------------------
@pytest.mark.usefixtures("authenticated_admin_user")
def test_dashboard_admin_get(client: Any) -> None:
    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    response = client.get(url_for('main.index'))

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert response.status_code == HTTPStatus.OK


def test_dashboard_no_authorize_get(client: Any) -> None:
    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    response = client.get(url_for('main.index'))

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert response.status_code == HTTPStatus.FOUND
    assert response.location.startswith(url_for('auth.login', _external=True))


@pytest.mark.usefixtures("authenticated_user")
def test_dashboard_user_get(client: Any) -> None:
    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    response = client.get(url_for('main.index'))

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert response.status_code == HTTPStatus.OK


@pytest.mark.usefixtures("authenticated_user")
def test_create_task(client: Any, sample_task_data: Dict) -> None:
    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    response = client.post(
        url_for("main.create_task"),
        json=sample_task_data
    )
    response_data = response.get_json()

    task_obj = models.Task.query.filter_by(
        title=sample_task_data["title"]
    ).first()

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert response.status_code == HTTPStatus.OK
    assert response_data["success"] is True
    assert response_data["id"] == task_obj.id
    assert response_data["title"] == task_obj.title
    assert response_data["description"] == task_obj.description
    assert response_data["status"] == task_obj.status
    assert response_data["due_date"] == task_obj.due_date.strftime("%Y-%m-%d")


@pytest.mark.usefixtures("authenticated_user")
def test_get_user_task_success(client: Any, sample_task_data: Dict) -> None:
    # -------------------------------------------------------------------------
    # --- Arrange ---
    # -------------------------------------------------------------------------
    saved_task = client.post(
        url_for("main.create_task"),
        json=sample_task_data
    ).get_json()

    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    task_obj = client.get(
        url_for("main.get_task", task_id=saved_task["id"])
    ).get_json()

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert task_obj is not None
    assert task_obj["title"] == saved_task["title"]
    assert task_obj["description"] == saved_task["description"]
    assert task_obj["status"] == saved_task["status"]
    assert task_obj["due_date"] == saved_task["due_date"]


@pytest.mark.usefixtures("authenticated_user")
def test_get_user_task_not_found(client: Any) -> None:
    # -------------------------------------------------------------------------
    # --- Arrange ---
    # -------------------------------------------------------------------------
    non_exist_id = 999999

    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    response = client.get(url_for("main.get_task", task_id=non_exist_id))

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.usefixtures("authenticated_user")
def test_get_other_user_task(
        client: Any, sample_other_user_task: models.Task
) -> None:
    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    response = client.get(url_for(
        "main.get_task", task_id=sample_other_user_task.id)
    )

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.usefixtures("authenticated_user")
def test_update_task(
        client: Any, sample_task_data: Dict, updated_task_data: Dict
) -> None:
    # -------------------------------------------------------------------------
    # --- Arrange ---
    # -------------------------------------------------------------------------
    create_resp = client.post(
        url_for("main.create_task"), json=sample_task_data
    )
    create_json = create_resp.get_json()
    task_id = create_json["id"]

    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    update_resp = client.put(
        url_for("main.update_task", task_id=task_id), json=updated_task_data,
    )
    update_json = update_resp.get_json()

    get_resp = client.get(url_for("main.get_task", task_id=task_id),)
    get_json = get_resp.get_json()

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert update_resp.status_code == HTTPStatus.OK
    assert update_json["success"] is True
    assert update_json["message"] == "Updated"
    assert get_json["title"] == updated_task_data["title"]
    assert get_json["description"] == updated_task_data["description"]
    assert get_json["status"] == updated_task_data["status"]
    assert get_json["due_date"] == updated_task_data["due_date"]


@pytest.mark.usefixtures("authenticated_user")
def test_update_task_other_user(
        client: Any, sample_other_user_task: models.Task,
        updated_task_data: Dict
) -> None:
    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    update_resp = client.put(
        url_for("main.update_task", task_id=sample_other_user_task.id),
        json=updated_task_data,
    )

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert update_resp.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.usefixtures("authenticated_user")
def test_delete_task(client: Any, sample_task_data: Dict) -> None:
    # -------------------------------------------------------------------------
    # --- Arrange ---
    # -------------------------------------------------------------------------
    create_resp = client.post(
        url_for("main.create_task"), json=sample_task_data,
    )
    create_json = create_resp.get_json()
    task_id = create_json["id"]

    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    delete_resp = client.delete(
        url_for("main.delete_task", task_id=task_id)
    )
    delete_json = delete_resp.get_json()

    get_resp = client.get(url_for("main.get_task", task_id=task_id))

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert delete_resp.status_code == HTTPStatus.OK
    assert delete_json["success"] is True
    assert delete_json["message"] == "Deleted"
    assert get_resp.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.usefixtures("authenticated_user")
def test_delete_task_other_user(
        client: Any, sample_other_user_task: models.Task
) -> None:
    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    delete_resp = client.delete(
        url_for("main.delete_task", task_id=sample_other_user_task.id)
    )

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert delete_resp.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.usefixtures("authenticated_user")
def test_set_status(client: Any, sample_task_data: Dict) -> None:
    # -------------------------------------------------------------------------
    # --- Arrange ---
    # -------------------------------------------------------------------------
    create_resp = client.post(
        url_for("main.create_task"), json=sample_task_data
    )
    create_json = create_resp.get_json()
    task_id = create_json["id"]
    new_status = next(s for s in TASK_STATUSES if s != create_json["status"])

    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    patch_resp = client.patch(
        url_for("main.set_status", task_id=task_id),
        json={"status": new_status},
    )
    patch_json = patch_resp.get_json()

    get_resp = client.get(url_for("main.get_task", task_id=task_id))
    get_json = get_resp.get_json()

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert patch_resp.status_code == HTTPStatus.OK
    assert patch_json["success"] is True
    assert patch_json["message"] == "Task marked as active"
    assert patch_json["status"] == new_status
    assert get_json["status"] == new_status


@pytest.mark.usefixtures("authenticated_user")
def test_set_status_other_user(
        client: Any, sample_other_user_task: models.Task
) -> None:
    # -------------------------------------------------------------------------
    # --- Arrange ---
    # -------------------------------------------------------------------------
    new_status = next(
        s for s in TASK_STATUSES if s != sample_other_user_task.status
    )

    # -------------------------------------------------------------------------
    # --- Act ---
    # -------------------------------------------------------------------------
    patch_resp = client.patch(
        url_for("main.set_status", task_id=sample_other_user_task.id),
        json={"status": new_status},
    )

    # -------------------------------------------------------------------------
    # --- Asserts ---
    # -------------------------------------------------------------------------
    assert patch_resp.status_code == HTTPStatus.FORBIDDEN
