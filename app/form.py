from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, FloatField, FileField, SelectField
from wtforms.validators import DataRequired, Email, Length, IPAddress


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')


class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('注册')


class ForgotPasswordForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    new_password = PasswordField('新密码', validators=[DataRequired()])
    submit = SubmitField('确认新密码')


# 定义文件上传表单
class UploadForm(FlaskForm):
    file = FileField('Excel 文件')
    submit = SubmitField('上传')


class SurveillanceSettingsForm(FlaskForm):
    camera_ip = StringField('摄像头 IP', validators=[DataRequired(), IPAddress()])
    rtsp_port = IntegerField('RTSP 端口', validators=[DataRequired()])
    username = StringField('用户名', validators=[DataRequired()])
    password = StringField('密码', validators=[DataRequired()])
    channel = IntegerField('通道号', validators=[DataRequired()])
    submit = SubmitField('保存设置')