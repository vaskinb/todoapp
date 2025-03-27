#!/usr/bin/env python
# coding: utf-8
# -----------------------------------------------------------------------------
# --- Flask Form ---
# -----------------------------------------------------------------------------
from flask_wtf import FlaskForm

# -----------------------------------------------------------------------------
# --- WTForms ---
# -----------------------------------------------------------------------------
from wtforms import PasswordField, BooleanField, SubmitField, StringField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo


class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[
        DataRequired(), Length(6, 20)
    ])
    remember_me = BooleanField('remember_me', validators=[Optional()])
    sign_in = SubmitField('Sign in')


class SignUpForm(FlaskForm):
    first_name = StringField(
        'First Name', validators=[DataRequired(), Length(2, 50)]
    )
    last_name = StringField(
        'Last Name', validators=[DataRequired(), Length(2, 50)]
    )
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(6, 20)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')
    ])
    sign_up = SubmitField('Sign Up')
