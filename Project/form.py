from flask_wtf import FlaskForm,RecaptchaField
from wtforms import StringField, PasswordField, BooleanField ,IntegerField, SubmitField
from wtforms.validators import InputRequired, Email, Length, EqualTo 
from flask_wtf.file import FileField,FileRequired



class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(min=4, max=40)])
    mobile = StringField('Mobile', validators=[InputRequired(), Length(min=10, max=10)])
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=25)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(),Length(min=8, max=25),EqualTo('password')])
    recaptcha = RecaptchaField()
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=25)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Sign In')

class EmailForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    submit = SubmitField('Password Reset Request')

  
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=25)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(),Length(min=8, max=25),EqualTo('password')])
    submit = SubmitField('Reset Password')

class UploadForm(FlaskForm):
    license = FileField('License',validators=[FileRequired()])
    
class UpdateProfile(FlaskForm):
    pic=FileField('Profile Picture',validators=[FileRequired()])
    submit = SubmitField('Update')
