import pymysql
from flask import Blueprint, render_template, redirect, url_for, flash, session
from app import db
from app.db import get_db_conn
from app.form import LoginForm, RegisterForm, ForgotPasswordForm
from app.utils import check_password, hash_password

bp = Blueprint('user', __name__, url_prefix='/user')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        connection = get_db_conn()
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "SELECT * FROM users WHERE username = %s"
                cursor.execute(sql, form.username.data)
                user = cursor.fetchone()
                print("111")
                print(user)
            if user and check_password(user['password_hash'], form.password.data):
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                session['role'] = user['role']
                flash('登录成功!', 'success')
                return redirect(url_for('user.dashboard'))  # 替换为实际仪表板路由
            else:
                flash('用户名、密码或角色错误', 'danger')
        except Exception as e:
            flash(f'登录错误: {str(e)}', 'danger')
        finally:
            connection.close()
    return render_template('user/login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        connection = get_db_conn()
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                # 检查用户名是否已存在
                sql = "SELECT * FROM users WHERE username = %s"
                cursor.execute(sql, (form.username.data,))
                if cursor.fetchone():
                    flash('用户名已存在', 'danger')
                    return render_template('register.html', form=form)
                # 检查邮箱是否已存在
                sql = "SELECT * FROM users WHERE email = %s"
                cursor.execute(sql, (form.email.data,))
                if cursor.fetchone():
                    flash('邮箱已被注册', 'danger')
                    return render_template('register.html', form=form)
                # 创建新用户
                hashed_pw = hash_password(form.password.data)
                role = 'student'
                sql = """
                INSERT INTO users 
                (username, full_name, email, password_hash, role) 
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    form.username.data,
                    form.full_name.data,
                    form.email.data,
                    hashed_pw,
                    role
                ))
                connection.commit()
                flash('注册成功! 请登录', 'success')
                return redirect(url_for('user.login'))
        except Exception as e:
            flash(f'注册失败: {str(e)}', 'danger')
        finally:
            connection.close()
    return render_template('user/register.html', form=form)


@bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        connection = get_db_conn()
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                # 验证用户名和邮箱是否匹配
                sql = "SELECT * FROM users WHERE username = %s AND email = %s"
                cursor.execute(sql, (form.username.data, form.email.data))
                user = cursor.fetchone()
                if user:
                    # 检查新密码是否与旧密码相同
                    if check_password(user['password_hash'], form.new_password.data):
                        flash('新密码不能与旧密码相同', 'danger')
                    else:
                        # 更新密码
                        hashed_pw = hash_password(form.new_password.data)
                        update_sql = "UPDATE users SET password_hash = %s WHERE user_id = %s"
                        cursor.execute(update_sql, (hashed_pw, user['user_id']))
                        connection.commit()
                        flash('密码重置成功！请使用新密码登录', 'success')
                        return redirect(url_for('user.login'))
                else:
                    flash('用户名或邮箱不匹配', 'danger')
        except Exception as e:
            flash(f'密码重置失败: {str(e)}', 'danger')
        finally:
            connection.close()
    return render_template('user/forget_password.html', form=form)


@bp.route('/logout')
def logout():
    session.clear()
    flash('您已成功登出', 'success')
    return redirect(url_for('login'))


@bp.route('/dashboard')
def dashboard():
    return redirect(url_for("student.dashboard"))
