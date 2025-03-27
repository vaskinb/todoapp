#!/usr/bin/env python
# coding: utf-8
import datetime
from collections import OrderedDict

# -----------------------------------------------------------------------------
# --- Typing ---
# -----------------------------------------------------------------------------
from typing import Dict

# -----------------------------------------------------------------------------
# --- Flask ---
# -----------------------------------------------------------------------------
from flask import render_template
from flask_login import login_required, current_user

# -----------------------------------------------------------------------------
# --- SQLAlchemy ---
# -----------------------------------------------------------------------------
from sqlalchemy import func

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
from app.main.views import statistic_bp


# -----------------------------------------------------------------------------
#  ______   ______  ______   ______  __   ______   ______  __   ______
# /\  ___\ /\__  _\/\  __ \ /\__  _\/\ \ /\  ___\ /\__  _\/\ \ /\  ___\
# \ \___  \\/_/\ \/\ \  __ \\/_/\ \/\ \ \\ \___  \\/_/\ \/\ \ \\ \ \____
#  \/\_____\  \ \_\ \ \_\ \_\  \ \_\ \ \_\\/\_____\  \ \_\ \ \_\\ \_____\
#   \/_____/   \/_/  \/_/\/_/   \/_/  \/_/ \/_____/   \/_/  \/_/ \/_____/

# -----------------------------------------------------------------------------
def count_tasks(user_id: int) -> Dict[str, int]:
    counts = {"total": 0, "pending": 0, "active": 0, "completed": 0}

    # -------------------------------------------------------------------------
    # --- Get count query ---
    # -------------------------------------------------------------------------
    counts_query = models.db.session.query(
        models.Task.status,
        func.count(models.Task.id)
    ).filter(
        models.Task.user_id == user_id
    ).group_by(
        models.Task.status
    ).all()

    # -------------------------------------------------------------------------
    # --- Count numbers of tasks ---
    # -------------------------------------------------------------------------
    for status, count in counts_query:
        counts["total"] += count
        counts[status] = count

    return counts


def get_daily_stats(user_id: int, start_day: datetime.date) -> OrderedDict:
    """ Daily statistics for the last 7 days """
    daily_data = OrderedDict()

    # -------------------------------------------------------------------------
    # --- Initialize date for periods ---
    # -------------------------------------------------------------------------
    end_day = start_day + datetime.timedelta(days=6)
    for i in range(7):
        day = start_day + datetime.timedelta(days=i)
        daily_data[day.isoformat()] = {"total": 0, "completed": 0}

    # -------------------------------------------------------------------------
    # --- Get tasks query ---
    # -------------------------------------------------------------------------
    daily_query = models.Task.get_daily_stats(user_id, start_day, end_day)

    # -------------------------------------------------------------------------
    # --- Fill data from query ---
    # -------------------------------------------------------------------------
    for day, total, completed in daily_query:
        day_str = day.isoformat()
        daily_data[day_str]["total"] = total
        daily_data[day_str]["completed"] = completed

    return daily_data


def get_weekly_stats(user_id: int, start_week: datetime.date) -> OrderedDict:
    """ Weekly statistics for the last 4 weeks"""
    weekly_data = OrderedDict()

    # -------------------------------------------------------------------------
    # --- Initialize week periods ---
    # -------------------------------------------------------------------------
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    weeks = []
    for i in range(4):
        week_start = monday - datetime.timedelta(weeks=i)
        week_end = week_start + datetime.timedelta(days=6)
        weeks.append((week_start, week_end))
    weeks = list(reversed(weeks))

    # -------------------------------------------------------------------------
    # --- Initialize data structure for each week ---
    # -------------------------------------------------------------------------
    for week_start, week_end in weeks:
        key = f"{week_start.isoformat()} - {week_end.isoformat()}"
        weekly_data[key] = {"total": 0, "completed": 0}

    # -------------------------------------------------------------------------
    # --- Get weekly task query ---
    # -------------------------------------------------------------------------
    weekly_query = models.Task.get_weekly_stats(user_id, start_week)

    # -------------------------------------------------------------------------
    # --- Fill data from query ---
    # -------------------------------------------------------------------------
    for week_start_date, total, completed in weekly_query:
        week_end_date = week_start_date + datetime.timedelta(days=6)
        key = f"{week_start_date.isoformat()} - {week_end_date.isoformat()}"
        if key in weekly_data:
            weekly_data[key]["total"] = total
            weekly_data[key]["completed"] = completed

    return weekly_data


def get_tasks_statistics(user_id: int) -> Dict:
    # -------------------------------------------------------------------------
    # --- Aggregate task statistics ---
    # -------------------------------------------------------------------------
    counts = count_tasks(user_id)
    today = datetime.date.today()
    start_day = today - datetime.timedelta(days=6)
    daily_data = get_daily_stats(user_id, start_day)

    # -------------------------------------------------------------------------
    # --- Determine the start_week for weekly statistics ---
    # -------------------------------------------------------------------------
    monday = today - datetime.timedelta(days=today.weekday())
    weeks = [monday - datetime.timedelta(weeks=i) for i in range(4)]
    start_week = min(weeks)
    weekly_data = get_weekly_stats(user_id, start_week)

    # -------------------------------------------------------------------------
    # --- Prepare final data structure ---
    # -------------------------------------------------------------------------
    stat = {
        "counts": counts,
        "daily": {
            "labels": list(daily_data.keys()),
            "total": [daily_data[label]["total"] for label in daily_data],
            "completed": [
                daily_data[label]["completed"] for label in daily_data
            ],
        },
        "weekly": {
            "labels": list(weekly_data.keys()),
            "total": [weekly_data[label]["total"] for label in weekly_data],
            "completed": [
                weekly_data[label]["completed"] for label in weekly_data
            ],
        },
    }
    return stat


@statistic_bp.route("/statistic", methods=["GET"])
@login_required
def main() -> str:
    # -------------------------------------------------------------------------
    # --- Get user stat ---
    # -------------------------------------------------------------------------
    stat = get_tasks_statistics(current_user.id)

    return render_template("statistic/statistic.html", stat=stat)

