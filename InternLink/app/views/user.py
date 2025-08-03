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
            if user and check_password(user['password_hash'], form.password.data):
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                session['role'] = user['role']
                print(session)
                flash('Login successful!', 'success')
                return redirect(url_for('user.dashboard'))  # Replace with the actual dashboard route
            else:
                flash('Incorrect username, password, or role', 'danger')
        except Exception as e:
            flash(f'Login error: {str(e)}', 'danger')
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
                # Check if the username already exists
                sql = "SELECT * FROM users WHERE username = %s"
                cursor.execute(sql, (form.username.data,))
                if cursor.fetchone():
                    flash('Username already exists', 'danger')
                    return render_template('register.html', form=form)
                # Check if the email is already registered
                sql = "SELECT * FROM users WHERE email = %s"
                cursor.execute(sql, (form.email.data,))
                if cursor.fetchone():
                    flash('Email is already registered', 'danger')
                    return render_template('register.html', form=form)
                # Create a new user
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
                flash('Registration successful! Please log in', 'success')
                return redirect(url_for('user.login'))
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')
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
                # Verify if the username and email match
                sql = "SELECT * FROM users WHERE username = %s AND email = %s"
                cursor.execute(sql, (form.username.data, form.email.data))
                user = cursor.fetchone()
                if user:
                    # Check if the new password is the same as the old password
                    if check_password(user['password_hash'], form.new_password.data):
                        flash('The new password cannot be the same as the old password', 'danger')
                    else:
                        # Update the password
                        hashed_pw = hash_password(form.new_password.data)
                        update_sql = "UPDATE users SET password_hash = %s WHERE user_id = %s"
                        cursor.execute(update_sql, (hashed_pw, user['user_id']))
                        connection.commit()
                        flash('Password reset successful! Please log in with the new password', 'success')
                        return redirect(url_for('user.login'))
                else:
                    flash('Username or email does not match', 'danger')
        except Exception as e:
            flash(f'Password reset failed: {str(e)}', 'danger')
        finally:
            connection.close()
    return render_template('user/forget_password.html', form=form)


@bp.route('/logout')
def logout():
    session.clear()
    flash('You have successfully logged out', 'success')
    return redirect(url_for('user.login'))


@bp.route('/dashboard')
def dashboard():
    role = session['role']
    if role == 'student':
        return redirect(url_for("student.dashboard"))
    elif role == 'employer':
        return redirect(url_for("employer.dashboard"))
    else:
        return redirect(url_for("admin.dashboard"))
    

