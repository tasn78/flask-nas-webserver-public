from app import create_app, db
from app.models import User, File, Backup, SystemLog  # Import all your models

app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    print("Database tables created successfully!")

    # Create admin user
    admin = User(
        username="admin",
        email="admin@example.com",  #Update with admin password
        role="admin",
        permissions="read,write,edit,admin"
    )
    admin.set_password("root")  # Set a secure password

    # Add admin to database
    db.session.add(admin)
    db.session.commit()
    print("Admin user created successfully!")