from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user
from app import db
# from app.forms import LoginForm, RegisterForm, ForgotPasswordForm
# from app.views import capture
bp = Blueprint('student', __name__, url_prefix='/student')