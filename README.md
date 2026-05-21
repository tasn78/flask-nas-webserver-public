# Flask NAS Web Server

A full-featured Network Attached Storage (NAS) web server built with Python Flask, providing secure file management, user access control, system monitoring, and automated backups.

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.1.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚀 Features

### File Management
- Upload, download, and delete files
- Create, rename, and delete folders
- User-specific directories with shared folder access
- Admin access to all files and folders
- Secure path handling to prevent directory traversal

### User Management
- Create, modify, and delete user accounts
- Role-based access control (admin, user)
- Granular permissions (read, write, edit, admin)
- Automatic user directory creation
- Password hashing with Werkzeug security

### System Monitoring
- Real-time CPU, memory, and disk usage monitoring
- System logs with pagination and filtering
- Clear logs functionality
- Admin-only access to monitoring features

### Backup and Restore
- Schedule automatic backups (daily, weekly, monthly)
- Manual backup execution
- Database and file system backups to CSV
- Restore from previous backups
- Backup status tracking and logging

### Security Features
- Nginx reverse proxy with HTTPS support
- SSL/TLS encryption
- User authentication and authorization
- IP-based access restrictions
- Session management with Flask-Login
- CSRF protection with Flask-WTF
- Secure password storage

## 🛠️ Technology Stack

- **Backend**: Python 3.11, Flask 3.1.0
- **Database**: MySQL 8.0
- **ORM**: SQLAlchemy 2.0
- **Web Server**: Nginx (reverse proxy)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF, WTForms
- **Data Processing**: Pandas

## 📁 Project Structure
flask-nas-webserver/
├── app/
│   ├── auth/                 # Authentication blueprint
│   │   ├── init.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── backup/               # Backup management blueprint
│   │   ├── init.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── file_manager/         # File operations blueprint
│   │   ├── init.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── system_monitor/       # System monitoring blueprint
│   │   ├── init.py
│   │   └── routes.py
│   ├── user_manager/         # User management blueprint
│   │   ├── init.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── static/               # CSS, JS, images
│   │   ├── css/
│   │   └── js/
│   ├── templates/            # Jinja2 HTML templates
│   │   ├── auth/
│   │   ├── backup/
│   │   ├── file_manager/
│   │   ├── system_monitor/
│   │   ├── user_manager/
│   │   └── base.html
│   ├── init.py          # App factory
│   ├── models.py            # Database models
│   ├── decorators.py        # Custom decorators
│   └── filters.py           # Template filters
├── config.py                # Configuration
├── run.py                   # Application entry point
├── init_db.py              # Database initialization
├── create_admin.py         # Admin user creation utility
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore             # Git ignore rules
└── README.md

## 📋 Prerequisites

- Python 3.9 or higher
- MySQL 8.0 or higher
- Nginx (optional, for production deployment)
- Git

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/tasn78/flask-nas-webserver-public.git
cd flask-nas-webserver-public
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up MySQL Database

```sql
CREATE DATABASE nas_db;
CREATE USER 'nas_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON nas_db.* TO 'nas_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Configure Environment Variables

Copy `.env.example` to `.env` and update with your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```bash
SECRET_KEY=your-secret-key-here-generate-a-random-string
DATABASE_URL=mysql+pymysql://nas_user:your_secure_password@localhost/nas_db?charset=utf8mb4
UPLOAD_FOLDER=/path/to/your/nas/storage
```

**Generate a secure SECRET_KEY:**
```python
import secrets
print(secrets.token_hex(32))
```

### 6. Create Storage Directory

```bash
# Windows
mkdir C:\NAS_Storage

# macOS/Linux
mkdir -p /path/to/nas/storage
```

### 7. Initialize Database

```bash
python init_db.py
```

This creates all database tables, an admin user, and the directory structure (shared/ and users/ folders).

### 8. Run the Application

```bash
python run.py
```

The application will be accessible at `http://127.0.0.1:5000`

## 🔐 Default Credentials

After running `init_db.py`, log in with:

- **Username**: `admin`
- **Password**: `adminpassword`

⚠️ **CRITICAL**: Change this password immediately after first login!

## 📖 Usage

### For Administrators

1. **User Management**: Create users, assign roles and permissions
2. **File Access**: View and manage all user files and the shared folder
3. **System Monitoring**: Monitor server resources and view system logs
4. **Backup Management**: Schedule and execute backups, restore from backups

### For Regular Users

1. **My Files**: Access personal file storage in dedicated user directory
2. **Shared Folder**: Collaborate with other users via the shared folder
3. **File Operations**: Upload, download, organize, and delete files

## 🔒 Security Considerations

⚠️ **Important Security Notes**:

- Change default admin password immediately
- Use strong, unique passwords for all accounts
- Keep dependencies up to date: `pip install -U -r requirements.txt`
- Use HTTPS in production (not plain HTTP)
- Configure firewall rules appropriately
- Regularly backup your data
- Review system logs for suspicious activity
- Do not expose to the internet without proper security measures
- This is a development/educational project - conduct security audit before production use

### Recommended Production Setup

1. Use proper SSL certificates (Let's Encrypt)
2. Configure Nginx as reverse proxy
3. Set up firewall rules (ufw, firewalld)
4. Enable rate limiting
5. Implement fail2ban for brute force protection
6. Use environment variables for all sensitive data
7. Regular security updates

## 🚀 Production Deployment with Nginx

### 1. Install Nginx

```bash
# Ubuntu/Debian
sudo apt install nginx

# Windows
# Download from https://nginx.org/en/download.html
```

### 2. Configure Nginx

Create `/etc/nginx/sites-available/nas-server` (Linux) or edit `nginx.conf` (Windows):

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/ssl/certificate.crt;
    ssl_certificate_key /path/to/ssl/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Run with Production Server

```bash
# Install Gunicorn (Linux)
pip install gunicorn

# Run
gunicorn -w 4 -b 127.0.0.1:5000 "app:create_app()"

# Or use Waitress (Windows)
pip install waitress
waitress-serve --port=5000 app:create_app
```

## 🧪 Development

### Running in Development Mode

```bash
python run.py
```

Debug mode is enabled by default in `run.py`.

### Database Migrations

If you modify database models:

```bash
flask db init
flask db migrate -m "Description of changes"
flask db upgrade
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 style guide
- Add docstrings to functions
- Write meaningful commit messages
- Test your changes before submitting

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is provided as-is for educational and development purposes. The authors are not responsible for any data loss, security breaches, or other issues that may arise from using this software. Always ensure proper security measures are in place before deploying to production.

This is a development project and has not been audited for production security. Use at your own risk.

## 📞 Support

For issues, questions, or contributions:

- Open an issue on [GitHub Issues](https://github.com/tasn78/flask-nas-webserver-public/issues)
- Check existing issues before creating new ones

## 🙏 Acknowledgments

- Flask documentation and community
- Bootstrap for UI components
- MySQL and SQLAlchemy
- All contributors to this project

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Nginx Documentation](https://nginx.org/en/docs/)

---

**Note**: This is a development/educational project. Before deploying to production, conduct a thorough security audit and follow industry best practices for web application security.

Made using Flask
