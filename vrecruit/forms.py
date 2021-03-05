from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TextAreaField, RadioField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from vrecruit.models import User, Employer, Applicant


class RegistrationForm(FlaskForm):
    
    email = StringField('Email',validators=[DataRequired(), Email()])
    your_name = StringField('Fullname', validators=[DataRequired()])
    contact_number = StringField('Contact Number', validators=[DataRequired()])
    user_type = RadioField('Applying as:', choices=[('Employer','Employer'),('Applicant','Applicant')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):

    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class DetailsEmployer(FlaskForm):
    designation = SelectField(u'Designation', choices=[('CEO', 'CEO'), ('Co-Founder', 'Co-Founder'), ('Founder', 'Founder'), ('HR', 'HR') ], validators=[DataRequired()])
    company_name = StringField('Company Name', validators=[DataRequired()])
    company_website = StringField('Company Website', validators=[DataRequired()])
    company_address = StringField('Company Address', validators=[DataRequired()])
    company_logo = FileField('Company logo', validators=[FileAllowed(['jpg', 'jpeg', 'webp', 'png'])])
    submit = SubmitField('Submit')

class DetailsApplicant(FlaskForm):
    college_name = StringField('College Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
   # profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'webp', 'png'])])
    submit = SubmitField('Submit')

class PostJobForm(FlaskForm):
    job_type = SelectField(u'Job Type', choices=[('Fulltime', 'Fulltime'), ('Internship', 'Internship'), ('Part-time', 'Part-time'), ('Freenlancer', 'Freenlancer') ], validators=[DataRequired()])
    no_of_openings = IntegerField('No of Openings', validators=[DataRequired()])
    job_profile = StringField('Job Profile/Designation', validators=[DataRequired()])
    job_stipend = IntegerField('Stipend', validators=[DataRequired()])
    job_description = StringField('Job Description', validators=[DataRequired()])
    skills_required = StringField('Skills Required', validators=[DataRequired()])
    job_experience = StringField('Job Experience', validators=[DataRequired()])
    submit = SubmitField('Post Job')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
