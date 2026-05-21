# create_admin.py
from app import create_app, db
from app.models import User
import argparse

# run this script : python create_admin.py --username admin --email admin@example.com --password securepassword

def create_admin_user(username, email, password):
    app = create_app()
    with app.app_context():
        # Check if user already exists
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"User '{username}' already exists.")
            return

        # Create new admin user
        user = User(
            username=username,
            email=email,
            role='admin',
            permissions='read,write,edit,admin'
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        print(f"Admin user '{username}' created successfully.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create admin user')
    parser.add_argument('--username', required=True, help='Admin username')
    parser.add_argument('--email', required=True, help='Admin email')
    parser.add_argument('--password', required=True, help='Admin password')

    args = parser.parse_args()
    create_admin_user(args.username, args.email, args.password)