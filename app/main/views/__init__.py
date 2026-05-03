#!/usr/bin/env python
# coding: utf-8
from importlib import import_module

from flask import Blueprint

main_bp = Blueprint('main', __name__)
calendar_bp = Blueprint('calendar', __name__)
statistic_bp = Blueprint('statistic', __name__)

import_module("app.main.views.errors.errors")
