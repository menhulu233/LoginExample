import os

from app import db
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql

bp = Blueprint('admin', __name__, url_prefix='/admin')


def is_admin():
    """Verify if the current user is an admin"""
    return 'role' in session and session['role'] == 'admin'


@bp.before_request
def check_admin():
    """Check admin permissions"""
    if not is_admin():
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('auth.login'))


@bp.route('/dashboard')
def dashboard():
    """Admin dashboard"""
    # Fetch statistics
    try:
        connection = db.get_db_conn()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # User statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) AS total_users,
                    SUM(CASE WHEN role = 'student' THEN 1 ELSE 0 END) AS students,
                    SUM(CASE WHEN role = 'employer' THEN 1 ELSE 0 END) AS employers,
                    SUM(CASE WHEN role = 'admin' THEN 1 ELSE 0 END) AS admins,
                    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) AS active_users,
                    SUM(CASE WHEN status = 'inactive' THEN 1 ELSE 0 END) AS inactive_users
                FROM users
            """)
            user_stats = cursor.fetchone()

            # Internship statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) AS total_internships,
                    SUM(CASE WHEN deadline > CURDATE() THEN 1 ELSE 0 END) AS active_internships,
                    SUM(CASE WHEN deadline <= CURDATE() THEN 1 ELSE 0 END) AS expired_internships
                FROM internship
            """)
            internship_stats = cursor.fetchone()

            # Application statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) AS total_applications,
                    SUM(CASE WHEN status = 'submitted' THEN 1 ELSE 0 END) AS submitted,
                    SUM(CASE WHEN status = 'reviewed' THEN 1 ELSE 0 END) AS reviewed,
                    SUM(CASE WHEN status = 'accepted' THEN 1 ELSE 0 END) AS accepted,
                    SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) AS rejected
                FROM application
            """)
            application_stats = cursor.fetchone()

            return render_template('admin/dashboard.html',
                                   user_stats=user_stats,
                                   internship_stats=internship_stats,
                                   application_stats=application_stats)

    except Exception as e:
        flash(f'Failed to load data: {str(e)}', 'danger')
        return render_template('admin/dashboard.html')
    finally:
        connection.close()


@bp.route('/users')
def user_list():
    """User list management"""
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 15  # Display 15 records per page

    # Get filter parameters
    search = request.args.get('search', '')
    role = request.args.get('role', '')
    status = request.args.get('status', '')

    try:
        connection = db.get_db_conn()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Base query
            base_query = "SELECT * FROM users WHERE 1=1"
            params = []

            # Add filter conditions
            if search:
                base_query += " AND (username LIKE %s OR full_name LIKE %s OR email LIKE %s)"
                params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

            if role:
                base_query += " AND role = %s"
                params.append(role)

            if status:
                base_query += " AND status = %s"
                params.append(status)

            # Calculate total count
            count_query = "SELECT COUNT(*) AS total FROM (" + base_query + ") AS sub"
            cursor.execute(count_query, params)
            total_records = cursor.fetchone()['total']
            total_pages = (total_records + per_page - 1) // per_page

            # Add pagination
            base_query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            offset = (page - 1) * per_page
            params.extend([per_page, offset])

            # Fetch current page data
            cursor.execute(base_query, params)
            users = cursor.fetchall()

            # Role options
            role_options = [
                ('', 'All Roles'),
                ('student', 'Student'),
                ('employer', 'Employer'),
                ('admin', 'Admin')
            ]

            # Status options
            status_options = [
                ('', 'All Statuses'),
                ('active', 'Active'),
                ('inactive', 'Inactive')
            ]

            return render_template('admin/users.html',
                                   users=users,
                                   role_options=role_options,
                                   status_options=status_options,
                                   current_role=role,
                                   current_status=status,
                                   search_query=search,
                                   page=page,
                                   per_page=per_page,
                                   total_pages=total_pages,
                                   total_records=total_records)

    except Exception as e:
        flash(f'Failed to load user list: {str(e)}', 'danger')
        return render_template('admin/users.html', users=[])
    finally:
        connection.close()


@bp.route('/users/<int:user_id>/status', methods=['POST'])
def change_user_status(user_id):
    """Change user status"""
    new_status = request.form.get('status')

    if new_status not in ['active', 'inactive']:
        flash('Invalid status value', 'danger')
        return redirect(url_for('admin.user_list'))

    try:
        connection = db.get_db_conn()
        with connection.cursor() as cursor:
            # Update user status
            sql = "UPDATE users SET status = %s WHERE user_id = %s"
            cursor.execute(sql, (new_status, user_id))
            connection.commit()

            flash(f'User status has been {"activated" if new_status == "active" else "deactivated"}', 'success')
            return redirect(url_for('admin.user_list'))

    except Exception as e:
        flash(f'Failed to update user status: {str(e)}', 'danger')
        return redirect(url_for('admin.user_list'))
    finally:
        connection.close()


@bp.route('/profile/password', methods=['GET', 'POST'])
def change_password():
    """Change password"""
    user_id = session.get('user_id')

    try:
        connection = db.get_db_conn()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Fetch current user information
            sql = "SELECT * FROM users WHERE user_id = %s"
            cursor.execute(sql, (user_id,))
            user = cursor.fetchone()

            if not user:
                flash('User information not found', 'danger')
                return redirect(url_for('admin.dashboard'))

            if request.method == 'POST':
                current_password = request.form.get('current_password')
                new_password = request.form.get('new_password')
                confirm_password = request.form.get('confirm_password')

                # Verify current password
                if not check_password_hash(user['password_hash'], current_password):
                    flash('Current password is incorrect', 'danger')
                    return render_template('admin/change_password.html', user=user)

                # Verify new password
                if new_password != confirm_password:
                    flash('New password and confirm password do not match', 'danger')
                    return render_template('admin/change_password.html', user=user)

                # Verify password strength
                if len(new_password) < 8:
                    flash('Password must be at least 8 characters long', 'danger')
                    return render_template('admin/change_password.html', user=user)

                # Verify new password is not the same as the old password
                if check_password_hash(user['password_hash'], new_password):
                    flash('New password cannot be the same as the current password', 'danger')
                    return render_template('admin/change_password.html', user=user)

                # Update password
                new_password_hash = generate_password_hash(new_password)
                update_sql = "UPDATE users SET password_hash = %s WHERE user_id = %s"
                cursor.execute(update_sql, (new_password_hash, user_id))
                connection.commit()

                flash('Password has been updated', 'success')
                return redirect(url_for('admin.profile'))

            return render_template('admin/change_password.html', user=user)

    except Exception as e:
        flash(f'Failed to change password: {str(e)}', 'danger')
        return render_template('admin/change_password.html')
    finally:
        connection.close()


