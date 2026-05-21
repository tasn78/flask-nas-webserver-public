# app/user_manager/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SelectMultipleField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, ValidationError
from app.models import User


class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password',
                              validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('admin', 'Admin'), ('user', 'User')])
    permissions = SelectMultipleField('Permissions',
                                      choices=[('read', 'Read'),
                                               ('write', 'Write'),
                                               ('edit', 'Edit'),
                                               ('admin', 'Admin')])
    submit = SubmitField('Create User')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class EditUserForm(FlaskForm):
    id = HiddenField('ID')
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Optional()])
    password2 = PasswordField('Repeat Password',
                              validators=[EqualTo('password')])
    role = SelectField('Role', choices=[('admin', 'Admin'), ('user', 'User')])
    permissions = SelectMultipleField('Permissions',
                                      choices=[('read', 'Read'),
                                               ('write', 'Write'),
                                               ('edit', 'Edit'),
                                               ('admin', 'Admin')])
    submit = SubmitField('Update User')

    def validate_username(self, username):
        # Check if username exists and is not the current user's username
        user = User.query.filter_by(username=username.data).first()
        if user is not None and str(user.id) != self.id.data:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        # Check if email exists and is not the current user's email
        user = User.query.filter_by(email=email.data).first()
        if user is not None and str(user.id) != self.id.data:
            raise ValidationError('Please use a different email address.')