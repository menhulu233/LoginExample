import os

from app import db
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql

bp = Blueprint('admin', __name__, url_prefix='/admin')


def is_admin():
    """验证当前用户是否为管理员"""
    return 'role' in session and session['role'] == 'admin'


@bp.before_request
def check_admin():
    """检查管理员权限"""
    if not is_admin():
        flash('您没有访问此页面的权限', 'danger')
        return redirect(url_for('auth.login'))


@bp.route('/dashboard')
def dashboard():
    """管理员仪表板"""
    # 获取统计数据
    try:
        connection = db.get_db_conn()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 用户统计数据
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

            # 实习统计数据
            cursor.execute("""
                SELECT 
                    COUNT(*) AS total_internships,
                    SUM(CASE WHEN deadline > CURDATE() THEN 1 ELSE 0 END) AS active_internships,
                    SUM(CASE WHEN deadline <= CURDATE() THEN 1 ELSE 0 END) AS expired_internships
                FROM internship
            """)
            internship_stats = cursor.fetchone()

            # 申请统计数据
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
        flash(f'加载数据失败: {str(e)}', 'danger')
        return render_template('admin/dashboard.html')
    finally:
        connection.close()


@bp.route('/users')
def user_list():
    """用户列表管理"""
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = 15  # 每页显示15条记录

    # 获取筛选参数
    search = request.args.get('search', '')
    role = request.args.get('role', '')
    status = request.args.get('status', '')

    try:
        connection = db.get_db_conn()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 基础查询
            base_query = "SELECT * FROM users WHERE 1=1"
            params = []

            # 添加筛选条件
            if search:
                base_query += " AND (username LIKE %s OR full_name LIKE %s OR email LIKE %s)"
                params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

            if role:
                base_query += " AND role = %s"
                params.append(role)

            if status:
                base_query += " AND status = %s"
                params.append(status)

            # 计算总数
            count_query = "SELECT COUNT(*) AS total FROM (" + base_query + ") AS sub"
            cursor.execute(count_query, params)
            total_records = cursor.fetchone()['total']
            total_pages = (total_records + per_page - 1) // per_page

            # 添加分页
            base_query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            offset = (page - 1) * per_page
            params.extend([per_page, offset])

            # 获取当前页数据
            cursor.execute(base_query, params)
            users = cursor.fetchall()

            # 角色选项
            role_options = [
                ('', '所有角色'),
                ('student', '学生'),
                ('employer', '企业'),
                ('admin', '管理员')
            ]

            # 状态选项
            status_options = [
                ('', '所有状态'),
                ('active', '激活'),
                ('inactive', '禁用')
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
        flash(f'加载用户列表失败: {str(e)}', 'danger')
        return render_template('admin/users.html', users=[])
    finally:
        connection.close()


@bp.route('/users/<int:user_id>/status', methods=['POST'])
def change_user_status(user_id):
    """更改用户状态"""
    new_status = request.form.get('status')

    if new_status not in ['active', 'inactive']:
        flash('无效的状态值', 'danger')
        return redirect(url_for('admin.user_list'))

    try:
        connection = db.get_db_conn()
        with connection.cursor() as cursor:
            # 更新用户状态
            sql = "UPDATE users SET status = %s WHERE user_id = %s"
            cursor.execute(sql, (new_status, user_id))
            connection.commit()

            flash(f'用户状态已{"激活" if new_status == "active" else "禁用"}', 'success')
            return redirect(url_for('admin.user_list'))

    except Exception as e:
        flash(f'更新用户状态失败: {str(e)}', 'danger')
        return redirect(url_for('admin.user_list'))
    finally:
        connection.close()


@bp.route('/profile/password', methods=['GET', 'POST'])
def change_password():
    """修改密码"""
    user_id = session.get('user_id')

    try:
        connection = db.get_db_conn()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 获取当前用户信息
            sql = "SELECT * FROM users WHERE user_id = %s"
            cursor.execute(sql, (user_id,))
            user = cursor.fetchone()

            if not user:
                flash('未找到用户信息', 'danger')
                return redirect(url_for('admin.dashboard'))

            if request.method == 'POST':
                current_password = request.form.get('current_password')
                new_password = request.form.get('new_password')
                confirm_password = request.form.get('confirm_password')

                # 验证当前密码
                if not check_password_hash(user['password_hash'], current_password):
                    flash('当前密码不正确', 'danger')
                    return render_template('admin/change_password.html', user=user)

                # 验证新密码
                if new_password != confirm_password:
                    flash('新密码和确认密码不一致', 'danger')
                    return render_template('admin/change_password.html', user=user)

                # 验证密码强度
                if len(new_password) < 8:
                    flash('密码长度至少为8个字符', 'danger')
                    return render_template('admin/change_password.html', user=user)

                # 验证新密码是否与旧密码相同
                if check_password_hash(user['password_hash'], new_password):
                    flash('新密码不能与当前密码相同', 'danger')
                    return render_template('admin/change_password.html', user=user)

                # 更新密码
                new_password_hash = generate_password_hash(new_password)
                update_sql = "UPDATE users SET password_hash = %s WHERE user_id = %s"
                cursor.execute(update_sql, (new_password_hash, user_id))
                connection.commit()

                flash('密码已更新', 'success')
                return redirect(url_for('admin.profile'))

            return render_template('admin/change_password.html', user=user)

    except Exception as e:
        flash(f'修改密码失败: {str(e)}', 'danger')
        return render_template('admin/change_password.html')
    finally:
        connection.close()


