#!/usr/bin/env python
# coding: utf-8
import datetime

# -----------------------------------------------------------------------------
# --- Flask ---
# -----------------------------------------------------------------------------
from flask import render_template, jsonify, request, abort, Response
from flask_login import login_required, current_user

# -----------------------------------------------------------------------------
# --- Models ---
# -----------------------------------------------------------------------------
from app import models

# -----------------------------------------------------------------------------
# --- Errors ---
# -----------------------------------------------------------------------------
from app.main.views.errors import errors

# -----------------------------------------------------------------------------
# --- Blueprint ---
# -----------------------------------------------------------------------------
from app.main.views import main_bp
from app.main.views.forms import TaskForm


# -----------------------------------------------------------------------------
#
#  __    __     ______     __     __   __
# /\ "-./  \   /\  __ \   /\ \   /\ "-.\ \
# \ \ \-./\ \  \ \  __ \  \ \ \  \ \ \-.  \
#  \ \_\ \ \_\  \ \_\ \_\  \ \_\  \ \_\\"\_\
#   \/_/  \/_/   \/_/\/_/   \/_/   \/_/ \/_/
#
# -----------------------------------------------------------------------------
def get_user_task(task_id: int) -> models.Task:
    task = models.db.session.query(
        models.Task
    ).filter(
        models.Task.id == task_id
    ).first()
    if not task:
        abort(404)

    return task


@main_bp.route("/", methods=['GET'])
@login_required
def index() -> str:
    # -------------------------------------------------------------------------
    # --- Task Form ---
    # -------------------------------------------------------------------------
    form = TaskForm()

    # -------------------------------------------------------------------------
    # --- Get tasks query ---
    # -------------------------------------------------------------------------
    tasks = models.db.session.query(
        models.Task
    ).filter(
        models.Task.user_id == current_user.id
    ).order_by(
        models.Task.created_on.desc()
    ).all()

    return render_template("dashboard/index.html", tasks=tasks, form=form)


@main_bp.route("/tasks/add", methods=["POST"])
@login_required
def create_task() -> Response:
    # -------------------------------------------------------------------------
    # --- Parse data ---
    # -------------------------------------------------------------------------
    data = request.json
    due_date = data.get("due_date")

    # -------------------------------------------------------------------------
    # --- Save task ---
    # -------------------------------------------------------------------------
    task = models.Task(
        title=data["title"],
        description=data.get("description", ""),
        status=data.get("status", "pending"),
        due_date=datetime.datetime.strptime(
            due_date, "%Y-%m-%d"
        ) if due_date else None,
        user_id=current_user.id,
    )
    models.db.session.add(task)
    models.db.session.commit()

    return jsonify({
        "success": True,
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "due_date": task.due_date.strftime("%Y-%m-%d")
        if task.due_date else None
    })


@main_bp.route("/tasks/get/<int:task_id>", methods=["GET"])
@login_required
def get_task(task_id: int) -> Response:
    # -------------------------------------------------------------------------
    # --- Get task object ---
    # -------------------------------------------------------------------------
    task = get_user_task(task_id)

    # -------------------------------------------------------------------------
    # --- Validate access ---
    # -------------------------------------------------------------------------
    if task.user_id != current_user.id:
        abort(403)

    return jsonify({
        "success": True,
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "due_date": task.due_date.strftime("%Y-%m-%d"),
    })


@main_bp.route("/tasks/edit/<int:task_id>", methods=["PUT"])
@login_required
def update_task(task_id: int) -> Response:
    # -------------------------------------------------------------------------
    # --- Get task object ---
    # -------------------------------------------------------------------------
    task = get_user_task(task_id)

    # -------------------------------------------------------------------------
    # --- Validate access ---
    # -------------------------------------------------------------------------
    if task.user_id != current_user.id:
        abort(403)

    # -------------------------------------------------------------------------
    # --- Parse data ---
    # -------------------------------------------------------------------------
    data = request.json
    task.title = data["title"]
    task.description = data.get("description", task.description)
    task.status = data.get("status", task.status)
    due_date = data.get("due_date")
    if due_date:
        task.due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d")

    # -------------------------------------------------------------------------
    # --- Update task ---
    # -------------------------------------------------------------------------
    models.db.session.merge(task)
    models.db.session.commit()

    return jsonify({
        "success": True,
        "message": "Updated"
    })


@main_bp.route("/tasks/delete/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id: int) -> Response:
    # -------------------------------------------------------------------------
    # --- Get task object ---
    # -------------------------------------------------------------------------
    task = get_user_task(task_id)

    # -------------------------------------------------------------------------
    # --- Validate access ---
    # -------------------------------------------------------------------------
    if task.user_id != current_user.id:
        abort(403)

    # -------------------------------------------------------------------------
    # --- Remove task ---
    # -------------------------------------------------------------------------
    models.db.session.delete(task)
    models.db.session.commit()

    return jsonify({
        "success": True,
        "message": "Deleted"
    })


@main_bp.route("/tasks/set_status/<int:task_id>", methods=["PATCH"])
@login_required
def set_status(task_id: int) -> Response:
    # -------------------------------------------------------------------------
    # --- Get task object ---
    # -------------------------------------------------------------------------
    task = get_user_task(task_id)

    # -------------------------------------------------------------------------
    # --- Validate access ---
    # -------------------------------------------------------------------------
    if task.user_id != current_user.id:
        abort(403)

    # -------------------------------------------------------------------------
    # --- Parse data ---
    # -------------------------------------------------------------------------
    data = request.json
    status = data.get("status", task.status)

    # -------------------------------------------------------------------------
    # --- Update status ---
    # -------------------------------------------------------------------------
    task.status = status
    models.db.session.merge(task)
    models.db.session.commit()

    return jsonify({
        "success": True,
        "message": "Task marked as active",
        "status": task.status
    })
