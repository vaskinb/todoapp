#!/usr/bin/env python
# coding: utf-8
import datetime

# -----------------------------------------------------------------------------
# --- Flask Form ---
# -----------------------------------------------------------------------------
from flask_wtf import FlaskForm

# -----------------------------------------------------------------------------
# --- WTForms ---
# -----------------------------------------------------------------------------
from wtforms import(
    StringField, SelectField
)
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Optional

# -----------------------------------------------------------------------------
# --- Utils ---
# -----------------------------------------------------------------------------
from app.utils.consts import TASK_STATUSES


class TaskForm(FlaskForm):
    title = StringField(
        'Title',
        validators=[DataRequired(), Length(max=255)]
    )
    description = StringField(
        'Description', validators=[Length(max=255)])
    status = SelectField(
        'Status',
        choices=[(status, status.capitalize()) for status in TASK_STATUSES],
        validators=[DataRequired()]
    )
    due_date = DateField(
        'Due Date',
        format='%Y-%m-%d',
        default=datetime.date.today,
        validators=[Optional()]
    )
