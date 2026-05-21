# app/scheduler.py
import os
import shutil
import datetime
import time
import schedule
import threading
from app import create_app, db
from app.models import Backup, SystemLog


def run_scheduled_backups():
    """Execute all scheduled backups."""
    app = create_app()
    with app.app_context():
        backups = Backup.query.filter_by(status='pending').all()
        for backup in backups:
            try:
                # Create destination directory if it doesn't exist
                if not os.path.exists(backup.destination_path):
                    os.makedirs(backup.destination_path)

                # Create timestamped backup folder
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_dir = os.path.join(backup.destination_path, f"backup_{timestamp}")

                # Copy files
                shutil.copytree(backup.source_path, backup_dir)

                # Update backup status
                backup.last_run = datetime.datetime.now()
                backup.status = 'success'

                # Add system log
                log = SystemLog(
                    log_type='info',
                    message=f"Scheduled backup '{backup.name}' completed successfully"
                )

                db.session.add(log)
                db.session.commit()
            except Exception as e:
                backup.status = 'failed'
                log = SystemLog(
                    log_type='error',
                    message=f"Scheduled backup '{backup.name}' failed: {str(e)}"
                )

                db.session.add(log)
                db.session.commit()


def start_scheduler():
    # Schedule daily backups at 2:00 AM
    schedule.every().day.at("02:00").do(run_scheduled_backups)

    # Start the scheduler in a separate thread
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()