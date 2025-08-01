import math

import pymysql
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from app import db

# from app.forms import LoginForm, RegisterForm, ForgotPasswordForm
# from app.views import capture
bp = Blueprint('employer', __name__, url_prefix='/employer')


def get_current_employer_id(user_id):
    """获取当前企业的ID"""
    try:
        connection = db.get_db_conn()
        with connection.cursor() as cursor:
            sql = "SELECT emp_id FROM employer WHERE user_id = %s"
            cursor.execute(sql, (user_id,))
            employer = cursor.fetchone()
            return employer['emp_id'] if employer else None
    except Exception as e:
        print(f"获取企业ID失败: {str(e)}")
        return None
    finally:
        connection.close()


@bp.route('/internships', methods=['GET'])
def internships():
    """企业实习列表"""
    if 'user_id' not in session or session.get('role') != 'employer':
        return redirect(url_for('user.login'))

    user_id = session['user_id']
    employer_id = get_current_employer_id(user_id)

    if not employer_id:
        flash('未找到企业信息', 'danger')
        return redirect(url_for('employer.dashboard'))

    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = 10  # 每页显示10条记录

    # 获取筛选参数
    search = request.args.get('search', '')
    status = request.args.get('status', '')  # 可选：active, expired

    try:
        connection = db.get_db_conn
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 基础查询
            base_query = """
                SELECT i.*, 
                       COUNT(a.application_id) AS application_count,
                       SUM(CASE WHEN a.status = 'accepted' THEN 1 ELSE 0 END) AS accepted_count,
                       CASE 
                         WHEN i.deadline < CURDATE() THEN 'expired'
                         ELSE 'active'
                       END AS status
                FROM internship i
                LEFT JOIN application a ON i.internship_id = a.internship_id
                WHERE i.company_id = %s
            """
            params = [employer_id]

            # 添加筛选条件
            if search:
                base_query += " AND i.title LIKE %s"
                params.append(f"%{search}%")

            if status:
                base_query += " HAVING status = %s"
                params.append(status)
            else:
                base_query += " GROUP BY i.internship_id"

            # 计算总数
            count_query = "SELECT COUNT(*) AS total FROM (" + base_query + ") AS sub"
            cursor.execute(count_query, params)
            total_records = cursor.fetchone()['total']
            total_pages = math.ceil(total_records / per_page)

            # 添加分页
            base_query += " ORDER BY i.created_at DESC LIMIT %s OFFSET %s"
            offset = (page - 1) * per_page
            params.extend([per_page, offset])

            # 获取当前页数据
            cursor.execute(base_query, params)
            internships = cursor.fetchall()

            # 获取企业信息（用于页面显示公司名称）
            sql = "SELECT company_name FROM employer WHERE emp_id = %s"
            cursor.execute(sql, (employer_id,))
            company = cursor.fetchone()

            return render_template('employer/internships.html',
                                   internships=internships,
                                   company=company,
                                   search_query=search,
                                   status_filter=status,
                                   page=page,
                                   per_page=per_page,
                                   total_pages=total_pages,
                                   total_records=total_records)

    except Exception as e:
        flash(f'加载实习信息失败: {str(e)}', 'danger')
        return render_template('employer/internships.html', internships=[])
    finally:
        connection.close()


@bp.route('/applications', methods=['GET'])
def applications():
    """企业申请管理"""
    if 'user_id' not in session or session.get('role') != 'employer':
        return redirect(url_for('user.login'))

    user_id = session['user_id']
    employer_id = get_current_employer_id(user_id)

    if not employer_id:
        flash('未找到企业信息', 'danger')
        return redirect(url_for('employer.dashboard'))

    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = 10  # 每页显示10条记录

    # 获取筛选参数
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    internship_id = request.args.get('internship', '')

    try:
        connection = db.get_db_conn
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 基础查询
            base_query = """
                SELECT a.*, 
                       i.title AS internship_title,
                       s.university, s.course,
                       u.full_name AS student_name,
                       u.profile_image,
                       CASE 
                         WHEN a.status = 'submitted' THEN '已提交'
                         WHEN a.status = 'reviewed' THEN '已查看'
                         WHEN a.status = 'accepted' THEN '已录取'
                         WHEN a.status = 'rejected' THEN '未录取'
                       END AS status_text
                FROM application a
                JOIN internship i ON a.internship_id = i.internship_id
                JOIN student s ON a.student_id = s.student_id
                JOIN users u ON s.user_id = u.user_id
                WHERE i.company_id = %s
            """
            params = [employer_id]

            # 添加筛选条件
            if status:
                base_query += " AND a.status = %s"
                params.append(status)

            if internship_id:
                base_query += " AND a.internship_id = %s"
                params.append(internship_id)

            if search:
                base_query += " AND (u.full_name LIKE %s OR i.title LIKE %s)"
                params.extend([f"%{search}%", f"%{search}%"])

            # 计算总数
            count_query = "SELECT COUNT(*) AS total FROM (" + base_query + ") AS sub"
            cursor.execute(count_query, params)
            total_records = cursor.fetchone()['total']
            total_pages = math.ceil(total_records / per_page)

            # 添加分页
            base_query += " ORDER BY a.applied_at DESC LIMIT %s OFFSET %s"
            offset = (page - 1) * per_page
            params.extend([per_page, offset])

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

            # 获取企业发布的实习职位（用于筛选）
            sql = "SELECT internship_id, title FROM internship WHERE company_id = %s"
            cursor.execute(sql, (employer_id,))
            internships = cursor.fetchall()

            return render_template('employer/applications.html',
                                   applications=applications,
                                   internships=internships,
                                   status_options=status_options,
                                   current_status=status,
                                   current_internship=internship_id,
                                   search_query=search,
                                   page=page,
                                   per_page=per_page,
                                   total_pages=total_pages,
                                   total_records=total_records)

    except Exception as e:
        flash(f'加载申请信息失败: {str(e)}', 'danger')
        return render_template('employer/applications.html', applications=[])
    finally:
        connection.close()


@bp.route('/applications/<int:application_id>', methods=['GET', 'POST'])
def application_detail(application_id):
    """申请详情与处理"""
    if 'user_id' not in session or session.get('role') != 'employer':
        return redirect(url_for('user.login'))

    user_id = session['user_id']
    employer_id = get_current_employer_id(user_id)

    if not employer_id:
        flash('未找到企业信息', 'danger')
        return redirect(url_for('employer.dashboard'))

    try:
        connection = db.get_db_conn
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 获取申请详情
            sql = """
                SELECT a.*, 
                       i.title AS internship_title, i.description AS internship_description,
                       s.university, s.course, s.resume_path,
                       u.full_name AS student_name, u.email AS student_email,
                       e.company_name
                FROM application a
                JOIN internship i ON a.internship_id = i.internship_id
                JOIN student s ON a.student_id = s.student_id
                JOIN users u ON s.user_id = u.user_id
                JOIN employer e ON i.company_id = e.emp_id
                WHERE a.application_id = %s AND i.company_id = %s
            """
            cursor.execute(sql, (application_id, employer_id))
            application = cursor.fetchone()

            if not application:
                flash('申请不存在或您无权访问', 'danger')
                return redirect(url_for('employer.applications'))

            # 如果是POST请求，更新申请状态
            if request.method == 'POST':
                action = request.form.get('action')
                feedback = request.form.get('feedback', '')

                if action in ['accept', 'reject']:
                    new_status = 'accepted' if action == 'accept' else 'rejected'

                    # 更新申请状态
                    update_sql = """
                        UPDATE application 
                        SET status = %s, feedback = %s 
                        WHERE application_id = %s
                    """
                    cursor.execute(update_sql, (new_status, feedback, application_id))
                    connection.commit()

                    flash(f'申请已{"接受" if action == "accept" else "拒绝"}', 'success')
                    return redirect(url_for('employer.application_detail', application_id=application_id))

            return render_template('employer/application_detail.html', application=application)

    except Exception as e:
        flash(f'处理申请失败: {str(e)}', 'danger')
        return redirect(url_for('employer.applications'))
    finally:
        connection.close()


@bp.route('/internships/new', methods=['GET', 'POST'])
def new_internship():
    """发布新实习"""
    if 'user_id' not in session or session.get('role') != 'employer':
        return redirect(url_for('user.login'))

    user_id = session['user_id']
    employer_id = get_current_employer_id(user_id)

    if not employer_id:
        flash('未找到企业信息', 'danger')
        return redirect(url_for('employer.dashboard'))

    if request.method == 'POST':
        # 获取表单数据
        title = request.form.get('title')
        description = request.form.get('description')
        location = request.form.get('location')
        duration = request.form.get('duration')
        skills_required = request.form.get('skills_required')
        deadline = request.form.get('deadline')
        stipend = request.form.get('stipend')
        number_of_opening = request.form.get('number_of_opening')
        additional_req = request.form.get('additional_req')

        # 验证数据
        if not title or not description:
            flash('标题和描述是必填项', 'danger')
            return render_template('employer/internship_form.html')

        try:
            connection = db.get_db_conn
            with connection.cursor() as cursor:
                # 插入新实习
                sql = """
                    INSERT INTO internship (
                        company_id, title, description, location, duration, 
                        skills_required, deadline, stipend, number_of_opening, additional_req
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    employer_id, title, description, location, duration,
                    skills_required, deadline, stipend, number_of_opening, additional_req
                ))
                connection.commit()

                flash('实习岗位发布成功!', 'success')
                return redirect(url_for('employer.internships'))

        except Exception as e:
            flash(f'发布实习失败: {str(e)}', 'danger')
            return render_template('employer/internship_form.html')
        finally:
            connection.close()

    return render_template('employer/internship_form.html')


@bp.route('/internships/<int:internship_id>', methods=['GET'])
def internship_detail(internship_id):
    """实习详情"""
    if 'user_id' not in session or session.get('role') != 'employer':
        return redirect(url_for('user.login'))

    user_id = session['user_id']
    employer_id = get_current_employer_id(user_id)

    if not employer_id:
        flash('未找到企业信息', 'danger')
        return redirect(url_for('employer.dashboard'))

    try:
        connection = db.get_db_conn
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 获取实习详情
            sql = """
                SELECT i.*, e.company_name,
                       COUNT(a.application_id) AS application_count,
                       SUM(CASE WHEN a.status = 'accepted' THEN 1 ELSE 0 END) AS accepted_count
                FROM internship i
                JOIN employer e ON i.company_id = e.emp_id
                LEFT JOIN application a ON i.internship_id = a.internship_id
                WHERE i.internship_id = %s AND i.company_id = %s
                GROUP BY i.internship_id
            """
            cursor.execute(sql, (internship_id, employer_id))
            internship = cursor.fetchone()

            if not internship:
                flash('实习不存在或您无权访问', 'danger')
                return redirect(url_for('employer.internships'))

            # 获取申请者列表
            sql = """
                SELECT a.*, u.full_name AS student_name, u.profile_image,
                       s.university, s.course,
                       CASE 
                         WHEN a.status = 'submitted' THEN '已提交'
                         WHEN a.status = 'reviewed' THEN '已查看'
                         WHEN a.status = 'accepted' THEN '已录取'
                         WHEN a.status = 'rejected' THEN '未录取'
                       END AS status_text
                FROM application a
                JOIN student s ON a.student_id = s.student_id
                JOIN users u ON s.user_id = u.user_id
                WHERE a.internship_id = %s
                ORDER BY a.applied_at DESC
            """
            cursor.execute(sql, (internship_id,))
            applications = cursor.fetchall()

            return render_template('employer/internship_detail.html',
                                   internship=internship,
                                   applications=applications)

    except Exception as e:
        flash(f'加载实习详情失败: {str(e)}', 'danger')
        return redirect(url_for('employer.internships'))
    finally:
        connection.close()
