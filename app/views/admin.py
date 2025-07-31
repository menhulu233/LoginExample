from flask import Blueprint, render_template, redirect, url_for, flash
from app import db
# from app.forms import LoginForm, RegisterForm, ForgotPasswordForm
# from app.views import capture
bp = Blueprint('admin', __name__, url_prefix='/admin')