# run.py
from app import create_app, db
from app.models import User, File, Backup, SystemLog
from flask import redirect, url_for
from flask_login import current_user

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'File': File, 'Backup': Backup, 'SystemLog': SystemLog}

@app.route('/')
def index():
    # If user is logged in, redirect to files
    if current_user.is_authenticated:
        return redirect(url_for('file_manager.index'))
    # Otherwise redirect to login
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True, host='0.0.0.0')