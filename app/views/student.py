import os
from math import ceil

import pymysql
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from werkzeug.utils import secure_filename

from app import db

# from app.forms import LoginForm, RegisterForm, ForgotPasswordForm
# from app.views import capture
from app.db import get_db_conn
from app.form import StudentForm, UserForm

bp = Blueprint('student', __name__, url_prefix='/student')


@bp.route('/dashboard')
def dashboard():
    # 获取学生相关数据（实际应用中需要实现）
    current_user = {}
    return render_template('admin/internship_management.html', current_user=current_user,application={})


@bp.route('/applications', methods=['GET'])
def applications():
    # 获取当前学生ID
    user_id = session['user_id']

    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = 10  # 每页显示10条记录

    # 获取筛选参数
    status = request.args.get('status', '')
    search = request.args.get('search', '')

    # 获取当前学生信息
    try:
        connection = get_db_conn()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 获取学生ID
            sql = "SELECT student_id FROM student WHERE user_id = %s"
            cursor.execute(sql, (user_id,))
            student = cursor.fetchone()

            # if not student:
            #     flash('未找到学生信息', 'danger')
            #     return redirect(url_for('student.dashboard'))
            student_id = student['student_id']
            # 构建基础查询
            base_query = """
                SELECT a.*, i.title, i.location, i.deadline, 
                       e.company_name, e.company_website,
                       CASE 
                         WHEN a.status = 'submitted' THEN '已提交'
                         WHEN a.status = 'reviewed' THEN '已查看'
                         WHEN a.status = 'accepted' THEN '已录取'
                         WHEN a.status = 'rejected' THEN '未录取'
                       END AS status_text
                FROM application a
                JOIN internship i ON a.internship_id = i.internship_id
                JOIN employer e ON i.company_id = e.emp_id
                WHERE a.student_id = %s
            """
            params = [student_id]

            # 添加筛选条件
            if status:
                base_query += " AND a.status = %s"
                params.append(status)

            if search:
                base_query += " AND (i.title LIKE %s OR e.company_name LIKE %s)"
                params.extend([f"%{search}%", f"%{search}%"])

            # 计算总数
            count_query = "SELECT COUNT(*) AS total FROM (" + base_query + ") AS sub"

            # 添加分页和排序
            base_query += " ORDER BY a.applied_at DESC"
            base_query += " LIMIT %s OFFSET %s"
            offset = (page - 1) * per_page
            params.extend([per_page, offset])

            # 获取总数
            cursor.execute(count_query, params[:-2])  # 排除分页参数
            total_records = cursor.fetchone()['total']
            total_pages = ceil(total_records / per_page)

            # 获取当前页数据
            cursor.execute(base_query, params)
            applications = cursor.fetchall()

            # 获取所有状态选项
            status_options = [
                ('', '所有状态'),
                ('submitted', '已提交'),
                ('reviewed', '已查看'),
                ('accepted', '已录取'),
                ('rejected', '未录取')
            ]

            return render_template('student/applications.html',
                                   applications=applications,
                                   status_options=status_options,
                                   current_status=status,
                                   search_query=search,
                                   page=page,
                                   per_page=per_page,
                                   total_pages=total_pages,
                                   total_records=total_records,
                                   current_user={})

    except Exception as e:
        flash(f'加载申请信息失败: {str(e)}', 'danger')
        return render_template('student/applications.html', applications=[], current_user={})
    finally:
        connection.close()


@bp.route('/applications/<int:internship_id>', methods=['GET'])
def application_detail(internship_id):
    # 获取当前学生ID
    user_id = session['user_id']

    try:
        connection = get_db_conn()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 获取学生ID
            sql = "SELECT student_id FROM student WHERE user_id = %s"
            cursor.execute(sql, (user_id,))
            student = cursor.fetchone()

            if not student:
                flash('未找到学生信息', 'danger')
                return redirect(url_for('student.applications'))

            student_id = student['student_id']

            # 获取申请详情
            sql = """
                SELECT a.*, i.title, i.description, i.location, i.duration, i.deadline, i.stipend,
                       e.company_name, e.company_description, e.company_website,
                       s.university, s.course, s.resume_path,
                       CASE 
                         WHEN a.status = 'submitted' THEN '已提交'
                         WHEN a.status = 'reviewed' THEN '已查看'
                         WHEN a.status = 'accepted' THEN '已录取'
                         WHEN a.status = 'rejected' THEN '未录取'
                       END AS status_text
                FROM application a
                JOIN internship i ON a.internship_id = i.internship_id
                JOIN employer e ON i.company_id = e.emp_id
                JOIN student s ON a.student_id = s.student_id
                WHERE a.student_id = %s AND a.internship_id = %s
            """
            cursor.execute(sql, (student_id, internship_id))
            application = cursor.fetchone()

            if not application:
                flash('未找到申请记录', 'danger')
                return redirect(url_for('student.applications'))

            # 格式化申请日期
            if application['applied_at']:
                application['applied_date'] = application['applied_at'].strftime('%Y年%m月%d日')

            return render_template('student/application_detail.html', application=application, current_user={})

    except Exception as e:
        flash(f'加载申请详情失败: {str(e)}', 'danger')
        return redirect(url_for('student.applications'))
    finally:
        connection.close()


@bp.route('/profile', methods=['GET', 'POST'])
def profile():
    # if 'user_id' not in session:
    #     flash('请先登录', 'danger')
    #     return redirect(url_for('user.login'))
    user_id = session['user_id']
    form = UserForm()
    try:
        connection = get_db_conn()
        with connection.cursor() as cursor:
            # 获取当前用户信息
            sql = "SELECT * FROM users WHERE user_id = %s"
            cursor.execute(sql, (user_id,))
            user = cursor.fetchone()

            if request.method == 'GET':
                # 填充表单
                form.username.data = user['username']
                form.full_name.data = user['full_name']
                form.email.data = user['email']
                form.role.data = user['role']
                form.status.data = user['status']

            if form.validate_on_submit():
                # 处理头像上传
                profile_image = form.profile_image.data
                profile_image_path = user['profile_image']  # 保留原路径

                if profile_image:
                    # 确保上传目录存在
                    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars')
                    os.makedirs(upload_dir, exist_ok=True)

                    # 生成安全文件名
                    filename = secure_filename(f"avatar_{user_id}_{profile_image.filename}")
                    file_path = os.path.join(upload_dir, filename)

                    # 保存文件
                    profile_image.save(file_path)
                    profile_image_path = f"uploads/avatars/{filename}"

                    # 删除旧头像（如果有）
                    if user['profile_image']:
                        old_path = os.path.join(current_app.root_path, 'static', user['profile_image'])
                        if os.path.exists(old_path):
                            os.remove(old_path)

                # 更新用户信息
                update_sql = """
                    UPDATE users 
                    SET username = %s, full_name = %s, email = %s, 
                        profile_image = %s, role = %s, status = %s
                    WHERE user_id = %s
                """
                cursor.execute(update_sql, (
                    form.username.data,
                    form.full_name.data,
                    form.email.data,
                    profile_image_path,
                    form.role.data,
                    form.status.data,
                    user_id
                ))
                connection.commit()

                # 更新session中的用户信息
                session['username'] = form.username.data
                session['full_name'] = form.full_name.data
                session['role'] = form.role.data

                flash('用户信息更新成功!', 'success')
                return redirect(url_for('student.profile'))
    except Exception as e:
        flash(f'更新用户信息失败: {str(e)}', 'danger')
    finally:
        connection.close()
    return render_template('student/user_profile.html', form=form, user=user,current_user={})


@bp.route('/profile_edit', methods=['GET', 'POST'])
def profile_edit():
    # if 'user_id' not in session:
    #     flash('请先登录', 'danger')
    #     return redirect(url_for('user.login'))
    #
    # if session.get('role') != 'student':
    #     flash('只有学生可以访问此页面', 'danger')
    #     return redirect(url_for('student.dashboard'))

    user_id = session['user_id']
    form = StudentForm()

    try:
        connection = get_db_conn()
        with connection.cursor() as cursor:
            # 获取学生信息
            sql = """
                SELECT s.*, u.username, u.full_name, u.email 
                FROM student s
                JOIN users u ON s.user_id = u.user_id
                WHERE s.user_id = %s
            """
            cursor.execute(sql, (user_id,))
            student = cursor.fetchone()

            # if not student:
            #     flash('未找到学生信息', 'danger')
            #     return redirect(url_for('student.dashboard'))

            if request.method == 'GET':
                # 填充表单
                form.university.data = student['university']
                form.course.data = student['course']

            if form.validate_on_submit():
                # 处理简历上传
                resume_file = form.resume.data
                resume_path = student['resume_path']  # 保留原路径

                if resume_file:
                    # 确保上传目录存在
                    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'resumes')
                    os.makedirs(upload_dir, exist_ok=True)

                    # 生成安全文件名
                    filename = secure_filename(f"resume_{user_id}_{resume_file.filename}")
                    file_path = os.path.join(upload_dir, filename)

                    # 保存文件
                    resume_file.save(file_path)
                    resume_path = f"uploads/resumes/{filename}"

                    # 删除旧简历（如果有）
                    if student['resume_path']:
                        old_path = os.path.join(current_app.root_path, 'static', student['resume_path'])
                        if os.path.exists(old_path):
                            os.remove(old_path)

                # 更新学生信息
                update_sql = """
                    UPDATE student 
                    SET university = %s, course = %s, resume_path = %s
                    WHERE user_id = %s
                """
                cursor.execute(update_sql, (
                    form.university.data,
                    form.course.data,
                    resume_path,
                    user_id
                ))
                connection.commit()

                flash('学生信息更新成功!', 'success')
                return redirect(url_for('student.profile_edit'))

    except Exception as e:
        flash(f'更新学生信息失败: {str(e)}', 'danger')
    finally:
        connection.close()

    return render_template('student/student_profile.html', form=form, student=student,current_user={})


@bp.route('/internships', methods=['GET'])
def internships():
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = 10  # 每页显示10条记录
    # 获取筛选参数
    location = request.args.get('location', '')
    duration = request.args.get('duration', '')
    # 构建基础查询
    base_query = """
        SELECT i.*, e.company_name 
        FROM internship i
        JOIN employer e ON i.company_id = e.emp_id
        WHERE i.deadline >= CURDATE()
    """
    params = []
    # 添加筛选条件
    if location:
        base_query += " AND i.location LIKE %s"
        params.append(f"%{location}%")
    if duration:
        base_query += " AND i.duration = %s"
        params.append(duration)
    # 计算总数
    count_query = "SELECT COUNT(*) AS total FROM (" + base_query + ") AS sub"
    # 添加分页和排序
    base_query += " ORDER BY i.deadline ASC"
    base_query += " LIMIT %s OFFSET %s"
    offset = (page - 1) * per_page
    params.extend([per_page, offset])
    try:
        connection = get_db_conn()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 获取总数
            cursor.execute(count_query, params[:-2])  # 排除分页参数
            total_records = cursor.fetchone()['total']
            total_pages = ceil(total_records / per_page)
            # 获取当前页数据
            cursor.execute(base_query, params)
            internships = cursor.fetchall()

            # 获取所有地点用于筛选
            cursor.execute("SELECT DISTINCT location FROM internship WHERE location IS NOT NULL AND location != ''")
            locations = [loc['location'] for loc in cursor.fetchall()]

            # 获取所有实习时长用于筛选
            cursor.execute("SELECT DISTINCT duration FROM internship WHERE duration IS NOT NULL AND duration != ''")
            durations = [dur['duration'] for dur in cursor.fetchall()]

        return render_template('student/internships.html',
                               internships=internships,
                               locations=locations,
                               durations=durations,
                               current_location=location,
                               current_duration=duration,
                               page=page,
                               per_page=per_page,
                               total_pages=total_pages,
                               total_records=total_records,current_user={})

    except Exception as e:
        flash(f'加载实习信息失败: {str(e)}', 'danger')
        return render_template('student/internships.html', internships=[], current_user={})
    finally:
        connection.close()


@bp.route('/internships/<int:internship_id>', methods=['GET'])
def internship_detail(internship_id):
    try:
        connection = get_db_conn()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 获取实习详情
            sql = """
                SELECT i.*, e.company_name, e.company_description, e.company_website
                FROM internship i
                JOIN employer e ON i.company_id = e.emp_id
                WHERE i.internship_id = %s
            """
            cursor.execute(sql, (internship_id,))
            internship = cursor.fetchone()

            if not internship:
                flash('未找到该实习岗位', 'danger')
                return redirect(url_for('student.internships'))

            # 检查用户是否已申请该实习
            student_id = session.get('student_id')  # 假设session中存储了student_id
            if student_id:
                check_sql = """
                    SELECT application_id, status 
                    FROM application 
                    WHERE student_id = %s AND internship_id = %s
                """
                cursor.execute(check_sql, (student_id, internship_id))
                application = cursor.fetchone()
                if application:
                    internship['applied'] = True
                    internship['application_status'] = application['status']
                else:
                    internship['applied'] = False

            return render_template('student/internship_detail.html', internship=internship, current_user={})

    except Exception as e:
        flash(f'加载实习详情失败: {str(e)}', 'danger')
        return redirect(url_for('student.internships'))
    finally:
        connection.close()
