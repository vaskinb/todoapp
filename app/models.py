#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

# -----------------------------------------------------------------------------
# --- Typing ---
# -----------------------------------------------------------------------------
from typing import List

# -----------------------------------------------------------------------------
# --- SQLAlchemy ---
# -----------------------------------------------------------------------------
from sqlalchemy.orm import relationship

# -----------------------------------------------------------------------------
# --- Flask ---
# -----------------------------------------------------------------------------
from flask_login import UserMixin

# -----------------------------------------------------------------------------
# --- Werkzeug ---
# -----------------------------------------------------------------------------
from werkzeug.security import generate_password_hash, check_password_hash

# -----------------------------------------------------------------------------
# --- SQLAlchemy ---
# -----------------------------------------------------------------------------
from flask_sqlalchemy import SQLAlchemy

# -----------------------------------------------------------------------------
# --- App ---
# -----------------------------------------------------------------------------
db = SQLAlchemy()


# -----------------------------------------------------------------------------
#  __  __     ______     ______     ______
# /\ \/\ \   /\  ___\   /\  ___\   /\  == \
# \ \ \_\ \  \ \___  \  \ \  __\   \ \  __<
#  \ \_____\  \/\_____\  \ \_____\  \ \_\ \_\
#   \/_____/   \/_____/   \/_____/   \/_/ /_/
#
# -----------------------------------------------------------------------------
class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # --- User Authentication fields ---
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)

    # --- User fields ---
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    role = db.Column(db.String, default="user", nullable=False)  # admin, user

    # --- Relationships ---
    tasks = relationship("Task", backref="user", cascade="all, delete")

    @property
    def password(self):
        raise AttributeError("password is not readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __str__(self):
        return f"<User {self.id}: {self.email}>"

    def __repr__(self):
        return self.__str__()


# -----------------------------------------------------------------------------
#  ______   ______     ______     __  __
# /\__  _\ /\  __ \   /\  ___\   /\ \/ /
# \/_/\ \/ \ \  __ \  \ \___  \  \ \  _"-.
#    \ \_\  \ \_\ \_\  \/\_____\  \ \_\ \_\
#     \/_/   \/_/\/_/   \/_____/   \/_/\/_/
#
# -----------------------------------------------------------------------------
class Task(db.Model):
    __tablename__ = "task"
    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    # --- Status: pending, active, completed ---
    status = db.Column(db.String(50), default="pending")

    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False,
    )

    @staticmethod
    def get_daily_stats(
        user_id: int, start_day: datetime.date, end_day: datetime.date
    ) -> List:
        sql = db.text("""
            SELECT 
              CAST(COALESCE(t.due_date, t.created_on) AS DATE) AS day,
              COUNT(t.id) AS total_tasks,
              SUM(
                CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END
              ) AS completed_tasks
            FROM task AS t
            WHERE t.user_id = :user_id
              AND CAST(
                COALESCE(t.due_date, t.created_on) AS DATE
              ) BETWEEN :start_day AND :end_day
            GROUP BY CAST(COALESCE(t.due_date, t.created_on) AS DATE);
        """)
        return db.engine.execute(
            sql, user_id=user_id, start_day=start_day, end_day=end_day
        ).fetchall()

    @staticmethod
    def get_weekly_stats(user_id: int, start_week: datetime.date) -> List:
        sql = db.text("""
            SELECT 
              CAST(
                date_trunc('week', COALESCE(t.due_date, t.created_on)) AS DATE
              ) AS week_start,
              COUNT(t.id) AS total_tasks,
              SUM(
                CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END
              ) AS completed_tasks
            FROM task AS t
            WHERE t.user_id = :user_id
              AND CAST(
                COALESCE(t.due_date, t.created_on) AS DATE
              ) >= :start_week
            GROUP BY CAST(
              date_trunc('week', COALESCE(t.due_date, t.created_on)) AS DATE
            );
        """)
        return db.engine.execute(
            sql, user_id=user_id, start_week=start_week
        ).fetchall()

    def __str__(self):
        return f"<Task {self.id}: {self.title}>"

    def __repr__(self):
        return self.__str__()
