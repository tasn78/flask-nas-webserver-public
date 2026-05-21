# init_directories.py
import os
from app import create_app
from app.models import User


def create_directory_structure():
    app = create_app()
    with app.app_context():
        # Get upload folder path from config
        upload_folder = app.config['UPLOAD_FOLDER']

        # Create main directories
        shared_dir = os.path.join(upload_folder, 'shared')
        users_dir = os.path.join(upload_folder, 'users')

        os.makedirs(shared_dir, exist_ok=True)
        os.makedirs(users_dir, exist_ok=True)

        # Create user directories
        users = User.query.all()
        for user in users:
            user_dir = os.path.join(users_dir, user.username)
            os.makedirs(user_dir, exist_ok=True)
            print(f"Created directory for user: {user.username}")

        print("Directory structure initialized successfully")


if __name__ == "__main__":
    create_directory_structure()