#!/usr/bin/env python
# coding: utf-8
from flask import Blueprint

main_bp = Blueprint('main', __name__)
calendar_bp = Blueprint('calendar', __name__)
statistic_bp = Blueprint('statistic', __name__)
