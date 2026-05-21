# app/backup/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired

class BackupForm(FlaskForm):
    name = StringField('Backup Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    source_path = StringField('Source Path', validators=[DataRequired()])
    destination_path = StringField('Destination Path', validators=[DataRequired()])
    schedule = SelectField('Schedule',
                         choices=[('daily', 'Daily'),
                                  ('weekly', 'Weekly'),
                                  ('monthly', 'Monthly')])
    submit = SubmitField('Create Backup')