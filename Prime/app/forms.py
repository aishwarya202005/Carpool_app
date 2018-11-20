from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo,ValidationError
from app.models import users
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    name = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    #gender = StringField('Gender',
    #                       validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Female', 'Female'), ('Male', 'Male'), ('Others', 'Others')])
    
    phoneNo = StringField('Phone No',
                            validators=[DataRequired(), Length(10)])
    dob = DateField('Date of Birth',format = '%Y-%m-%d',
                            validators=[DataRequired()])
    govtId = IntegerField('Government Id',
                            validators=[DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        user = users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email Id already exists. Please choose a different one.')
class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = users.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already exists.. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = users.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email id already exists.. Please choose a different one.')

