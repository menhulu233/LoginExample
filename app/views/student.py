from flask import Blueprint, render_template, redirect, url_for, flash
from app import db

# from app.forms import LoginForm, RegisterForm, ForgotPasswordForm
# from app.views import capture
bp = Blueprint('student', __name__, url_prefix='/student')


@bp.route('/dashboard')
def dashboard():
    # 获取学生相关数据（实际应用中需要实现）
    return render_template('student/dashboard.html')
