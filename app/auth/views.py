#!/usr/bin/env python
# coding: utf-8
# -----------------------------------------------------------------------------
# --- Flask ---
# -----------------------------------------------------------------------------
import flask_login
from flask import (render_template, redirect, url_for, Blueprint, request)
from flask_login import login_user

# -----------------------------------------------------------------------------
# --- Forms ---
# -----------------------------------------------------------------------------
from .forms import LoginForm, SignUpForm

# -----------------------------------------------------------------------------
# --- Models ---
# -----------------------------------------------------------------------------
from .. import models

# -----------------------------------------------------------------------------
# --- Blueprint ---
# -----------------------------------------------------------------------------
auth = Blueprint('auth', __name__)


# -----------------------------------------------------------------------------
#  __         ______     ______     __     __   __
# /\ \       /\  __ \   /\  ___\   /\ \   /\ "-.\ \
# \ \ \____  \ \ \/\ \  \ \ \__ \  \ \ \  \ \ \-.  \
#  \ \_____\  \ \_____\  \ \_____\  \ \_\  \ \_\\"\_\
#   \/_____/   \/_____/   \/_____/   \/_/   \/_/ \/_/
#
# -----------------------------------------------------------------------------
@auth.route('/login', methods=["GET", "POST"])
def login():
    # -------------------------------------------------------------------------
    # --- Form ---
    # -------------------------------------------------------------------------
    form = LoginForm()

    # -------------------------------------------------------------------------
    # --- Validate form ---
    # -------------------------------------------------------------------------
    if form.validate_on_submit():
        user_email = form.email.data.lower()
        user_password = form.password.data
        remember_me = form.remember_me.data

        # ---------------------------------------------------------------------
        # --- Try to get user ---
        # ---------------------------------------------------------------------
        user = models.User.query.filter_by(email=user_email).first()
        if user and user.verify_password(user_password):
            # -----------------------------------------------------------------
            # --- Auth user ---
            # -----------------------------------------------------------------
            login_user(user, remember_me)

            # -----------------------------------------------------------------
            # --- Redirect ---
            # -----------------------------------------------------------------
            return redirect(
                request.args.get('next') or url_for('main.index')
            )

        else:
            # -----------------------------------------------------------------
            # --- Wrong password ---
            # -----------------------------------------------------------------
            form.email.errors.append('Email or password are wrong')

    # -------------------------------------------------------------------------
    return render_template('auth/auth.html', form=form)


# -----------------------------------------------------------------------------
#  ______     __     ______     __   __        __  __     ______
# /\  ___\   /\ \   /\  ___\   /\ "-.\ \      /\ \/\ \   /\  == \
# \ \___  \  \ \ \  \ \ \__ \  \ \ \-.  \     \ \ \_\ \  \ \  _-/
#  \/\_____\  \ \_\  \ \_____\  \ \_\\"\_\     \ \_____\  \ \_\
#   \/_____/   \/_/   \/_____/   \/_/ \/_/      \/_____/   \/_/
#
# -----------------------------------------------------------------------------
@auth.route('/signup', methods=["GET", "POST"])
def signup():
    # -------------------------------------------------------------------------
    # --- Form ---
    # -------------------------------------------------------------------------
    form = SignUpForm()

    # -------------------------------------------------------------------------
    # --- Validate form ---
    # -------------------------------------------------------------------------
    if form.validate_on_submit():
        user_email = form.email.data
        user_password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        # ---------------------------------------------------------------------
        # --- Check if user exists ---
        # ---------------------------------------------------------------------
        existing_user = models.User.query.filter_by(email=user_email).first()
        if existing_user:
            form.email.errors.append('Email is already registered')
        else:
            # -----------------------------------------------------------------
            # --- Create new user ---
            # -----------------------------------------------------------------
            new_user = models.User(
                email=user_email,
                first_name=first_name,
                last_name=last_name,
                role='user',
            )
            new_user.password = user_password
            models.db.session.add(new_user)
            models.db.session.commit()

            # -----------------------------------------------------------------
            # --- Login user ---
            # -----------------------------------------------------------------
            login_user(new_user)

            # -----------------------------------------------------------------
            # --- Redirect ---
            # -----------------------------------------------------------------
            return redirect(url_for('main.index'))

    return render_template('auth/sign_up.html', form=form)


# -----------------------------------------------------------------------------
#  __         ______     ______     ______     __  __     ______
# /\ \       /\  __ \   /\  ___\   /\  __ \   /\ \/\ \   /\__  _\
# \ \ \____  \ \ \/\ \  \ \ \__ \  \ \ \/\ \  \ \ \_\ \  \/_/\ \/
#  \ \_____\  \ \_____\  \ \_____\  \ \_____\  \ \_____\    \ \_\
#   \/_____/   \/_____/   \/_____/   \/_____/   \/_____/     \/_/
#
# -----------------------------------------------------------------------------
@auth.route('/logout')
@flask_login.login_required
def logout():
    # -------------------------------------------------------------------------
    # --- Logout ---
    # -------------------------------------------------------------------------
    flask_login.logout_user()

    # -------------------------------------------------------------------------
    # --- Redirect ---
    # -------------------------------------------------------------------------
    return redirect(url_for('auth.login'))
