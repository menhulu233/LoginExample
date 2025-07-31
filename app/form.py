# 表单定义
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SelectField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')


class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[
        DataRequired(),
        Length(min=3, max=50)
    ])
    full_name = StringField('姓名', validators=[DataRequired()])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[
        DataRequired(),
        Length(min=6)
    ])
    confirm_password = PasswordField('确认密码', validators=[
        DataRequired(),
        EqualTo('password', message='两次密码必须一致')
    ])
    submit = SubmitField('注册')


class ForgotPasswordForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    new_password = PasswordField('新密码', validators=[
        DataRequired(),
        Length(min=6, message='密码长度至少为6个字符')
    ])
    confirm_password = PasswordField('确认新密码', validators=[
        DataRequired(),
        EqualTo('new_password', message='两次输入的密码必须一致')
    ])
    submit = SubmitField('重置密码')


class UserForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=50)])
    full_name = StringField('姓名', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    profile_image = FileField('头像', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], '只允许上传图片文件 (JPG, JPEG, PNG)')
    ])
    role = SelectField('角色', choices=[
        ('student', '学生'),
        ('employer', '企业'),
        ('admin', '管理员')
    ], validators=[DataRequired()])
    status = SelectField('状态', choices=[
        ('active', '活跃'),
        ('inactive', '停用')
    ], validators=[DataRequired()])
    submit = SubmitField('更新用户信息')


class StudentForm(FlaskForm):
    university = StringField('大学', validators=[DataRequired(), Length(min=2, max=100)])
    course = StringField('专业', validators=[DataRequired(), Length(min=2, max=100)])
    resume = FileField('简历 (PDF)', validators=[
        Optional(),
        FileAllowed(['pdf'], '只允许上传PDF文件')
    ])
    submit = SubmitField('更新学生信息')
