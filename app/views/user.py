from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user
from app import db
# from app.forms import LoginForm, RegisterForm, ForgotPasswordForm
bp = Blueprint('user', __name__, url_prefix='/user')


@bp.route('/', methods=['GET', 'POST'])
def index():
    return '<h1>Hello, World!</h1>'
# @bp.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first()
#         if user and user.password == form.password.data:
#             login_user(user)
#             return redirect(url_for('capture.index'))
#         flash('登录失败，用户名或密码错误！')
#     return render_template('login.html', form=form)
#
#
# @bp.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegisterForm()
#     if form.validate_on_submit():
#         new_user = User(
#             username=form.username.data,
#             email=form.email.data,
#             password=form.password.data
#         )
#         db.session.add(new_user)
#         db.session.commit()
#         flash('注册成功！','success')
#         return redirect(url_for('auth.login'))
#     return render_template('register.html', form=form)
#
#
# @bp.route('/forgot_password', methods=['GET', 'POST'])
# def forgot_password():
#     form = ForgotPasswordForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data, email=form.email.data).first()
#         if user:
#             user.password = form.new_password.data
#             db.session.commit()
#             flash('密码成功更新，请重新登录！','error')
#             return redirect(url_for('auth.login'))
#         else:
#             flash('用户名与邮箱不匹配！','error')
#     return render_template('forgot_password.html', form=form)
