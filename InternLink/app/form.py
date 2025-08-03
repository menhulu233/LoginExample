# Form definitions
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SelectField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=50)
    ])
    full_name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')


class ForgotPasswordForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')


class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    profile_image = FileField('Profile Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only image files (JPG, JPEG, PNG) are allowed')
    ])
    submit = SubmitField('Update User Information')


class StudentForm(FlaskForm):
    university = StringField('University', validators=[DataRequired(), Length(min=2, max=100)])
    course = StringField('Course', validators=[DataRequired(), Length(min=2, max=100)])
    resume = FileField('Resume (PDF)', validators=[
        Optional(),
        FileAllowed(['pdf'], 'Only PDF files are allowed')
    ])
    submit = SubmitField('Update Student Information')
