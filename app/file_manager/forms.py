# app/file_manager/forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class UploadFileForm(FlaskForm):
    file = FileField('File', validators=[FileRequired()])
    submit = SubmitField('Upload')

class CreateFolderForm(FlaskForm):
    folder_name = StringField('Folder Name', validators=[DataRequired()])
    submit = SubmitField('Create Folder')