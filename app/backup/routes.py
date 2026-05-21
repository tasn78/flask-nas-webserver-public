# app/backup/routes.py
import os
import shutil
import datetime
import subprocess
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.backup import bp
from app.models import Backup, SystemLog
from app.backup.forms import BackupForm
import MySQLdb as mdb
import pandas as pd
import re
import sys
import csv

from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import insert
from dateutil.parser import parse


def get_db_credentials():
    """Extract database credentials from config"""
    db_url = current_app.config['SQLALCHEMY_DATABASE_URI']
    # Parse URL: mysql+pymysql://user:password@host/database
    match = re.search(r'://(.+?):(.+?)@(.+?)/(.+?)\?', db_url)
    if match:
        return {
            'user': match.group(1),
            'password': match.group(2),
            'host': match.group(3),
            'database': match.group(4)
        }
    return {
        'user': 'nas_user',
        'password': 'your_password',
        'host': 'localhost',
        'database': 'nas_db'
    }


def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


def insert_on_conflict_update(table, conn, keys, data_iter):
    # update columns "b" and "c" on primary key conflict
    data = [dict(zip(keys, row)) for row in data_iter]
    stmt = (
        insert(table.table)
        .values(data)
    )
    stmt = stmt.on_duplicate_key_update(b=stmt.inserted.b, c=stmt.inserted.c)
    result = conn.execute(stmt)
    return result.rowcount


@bp.route('/')
@login_required
def index():
    if not current_user.has_permission('admin'):
        flash('Unauthorized access.')
        return redirect(url_for('file_manager.index'))

    backups = Backup.query.all()
    return render_template('backup/index.html', backups=backups)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.has_permission('admin'):
        flash('Unauthorized access.')
        return redirect(url_for('file_manager.index'))

    form = BackupForm()
    if form.validate_on_submit():
        backup = Backup(
            name=form.name.data,
            description=form.description.data,
            source_path=form.source_path.data,
            destination_path=form.destination_path.data,
            schedule=form.schedule.data,
            status='pending',
            user_id=current_user.id
        )

        db.session.add(backup)
        db.session.commit()

        flash('Backup scheduled successfully.')
        return redirect(url_for('backup.index'))

    return render_template('backup/create.html', form=form)


@bp.route('/run/<int:id>')
@login_required
def run_backup(id):
    if not current_user.has_permission('admin'):
        flash('Unauthorized access.')
        return redirect(url_for('file_manager.index'))

    backup = Backup.query.get_or_404(id)

    try:
        # Create destination directory if it doesn't exist
        if not os.path.exists(backup.destination_path):
            os.makedirs(backup.destination_path)

        # Create timestamped backup folder
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = os.path.join(backup.destination_path, f"backup_{timestamp}")

        # Copy files
        shutil.copytree(backup.source_path, backup_dir)

        # Get database credentials from config
        db_creds = get_db_credentials()

        # Create database connection string
        db_url = current_app.config['SQLALCHEMY_DATABASE_URI']

        # Connect to database
        mydb = mdb.connect(
            host=db_creds['host'],
            user=db_creds['user'],
            password=db_creds['password'],
            db=db_creds['database']
        )
        engine = create_engine(db_url)

        # Get a list of all tables in database
        tables = mydb.cursor()
        tables.execute("show tables")

        # for each table, dump it to csv file
        for table in tables:
            print(f"{table[0]}")

            query = f"select * from {table[0]}"
            data = mydb.cursor()
            data.execute(query)

            df = pd.read_sql(sql=query, con=engine)
            df.to_csv(f"{backup_dir}/{table[0]}.csv", index=False)
        tables.close()
        mydb.close()

        # Update backup status
        backup.last_run = datetime.datetime.now()
        backup.status = 'success'

        # Add system log
        log = SystemLog(
            log_type='info',
            message=f"Backup '{backup.name}' completed successfully"
        )

        db.session.add(log)
        db.session.commit()

        flash('Backup completed successfully.')
    except Exception as e:
        backup.status = 'failed'
        log = SystemLog(
            log_type='error',
            message=f"Backup '{backup.name}' failed: {str(e)}"
        )

        db.session.add(log)
        db.session.commit()

        flash(f'Backup failed: {str(e)}')

    return redirect(url_for('backup.index'))


@bp.route('/restore/<int:id>', methods=['GET'])
@login_required
def restore_backup(id):
    if not current_user.has_permission('admin'):
        flash('Unauthorized access.')
        return redirect(url_for('file_manager.index'))

    backup = Backup.query.get_or_404(id)

    try:
        # Check if backup folder exists
        if not os.path.exists(backup.destination_path):
            flash(f"Backup destination '{backup.destination_path}' not found.")
            return redirect(url_for('backup.index'))

        # Get active folder path from config
        active_folder_path = current_app.config['UPLOAD_FOLDER']

        # Restore files from backup destination to active folder
        timestamped_backup_folders = sorted(
            [folder for folder in os.listdir(backup.destination_path) if folder.startswith('backup_')],
            reverse=True
        )

        if timestamped_backup_folders:
            latest_backup = timestamped_backup_folders[0]
            backup_dir = os.path.join(backup.destination_path, latest_backup)

            # Check if the backup directory exists
            if not os.path.exists(backup_dir):
                flash(f"Backup folder '{latest_backup}' not found.")
                return redirect(url_for('backup.index'))

            # Ensure the active folder is empty before restoring
            if os.path.exists(active_folder_path):
                for item in os.listdir(active_folder_path):
                    item_path = os.path.join(active_folder_path, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)

            # Restore files from backup to active folder
            for item in os.listdir(backup_dir):
                source = os.path.join(backup_dir, item)
                destination = os.path.join(active_folder_path, item)

                if not destination.endswith('.csv'):
                    if os.path.isdir(source):
                        shutil.copytree(source, destination, dirs_exist_ok=True)
                    else:
                        shutil.copy2(source, destination)

            # ===============================
            # Restore tables from CSV
            # ===============================
            dump_file = os.path.join(backup_dir, 'file.csv')

            if os.path.exists(dump_file):
                # Get database credentials from config
                db_creds = get_db_credentials()
                db_url = current_app.config['SQLALCHEMY_DATABASE_URI']

                # Connect to database
                engine = create_engine(db_url)
                mydb = mdb.connect(
                    host=db_creds['host'],
                    user=db_creds['user'],
                    password=db_creds['password'],
                    db=db_creds['database']
                )

                # Get a list of all tables in database
                tables = mydb.cursor()
                tables.execute("show tables")

                # for each table, restore from csv
                for table in tables:
                    if f"{table[0]}" == 'backup':
                        continue
                    print(f"{table[0]}")

                    query = f"select * from {table[0]}"
                    data = mydb.cursor()
                    data.execute(query)

                    # delete table fields
                    tables.execute(f"DELETE FROM {table[0]};")
                    current_file = os.path.join(backup_dir, f'{table[0]}.csv')
                    print(current_file)

                    # restore from csv
                    with open(current_file, mode='r') as file:
                        csv_data = csv.reader(file)
                        table_fields = ''
                        separator = ','
                        for row in csv_data:
                            # save field names for each query
                            if row[0] == 'id':
                                table_fields = f'({separator.join(row)})'
                                continue
                            # formate fields for query
                            for i in range(len(row)):
                                row[i] = f'\'{row[i]}\''
                            print(row)
                            tables.execute(f'INSERT INTO {table[0]} {table_fields} VALUES ( {separator.join(row)} )')
                tables.close()
                mydb.close()

            else:
                flash(f"SQL dump file '{dump_file}' not found in backup directory.")

            # Update backup status
            backup.status = 'restored'
            backup.last_run = datetime.datetime.now()

            # Add system log for restore
            log = SystemLog(
                log_type='info',
                message=f"Backup '{backup.name}' restored successfully"
            )

            db.session.add(log)
            db.session.commit()

            flash('Backup restored successfully.')

        else:
            flash('No valid backup found to restore.')

    except Exception as e:
        backup.status = 'failed'
        log = SystemLog(
            log_type='error',
            message=f"Restore of backup '{backup.name}' failed: {str(e)}"
        )

        db.session.add(log)
        db.session.commit()

        flash(f'Restore failed: {str(e)}')

    return redirect(url_for('backup.index'))


@bp.route('/delete/<int:id>')
@login_required
def delete(id):
    if not current_user.has_permission('admin'):
        flash('Unauthorized access.')
        return redirect(url_for('file_manager.index'))

    backup = Backup.query.get_or_404(id)
    db.session.delete(backup)
    db.session.commit()

    flash('Backup schedule deleted.')
    return redirect(url_for('backup.index'))


@bp.route('/restore/<path:backup_path>')
@login_required
def restore(backup_path):
    if not current_user.has_permission('admin'):
        flash('Unauthorized access.')
        return redirect(url_for('file_manager.index'))

    # Get the original destination path from the backup path
    backup_dir = os.path.dirname(backup_path)
    backup = Backup.query.filter_by(destination_path=backup_dir).first()

    if not backup:
        flash('Backup not found.')
        return redirect(url_for('backup.index'))

    try:
        # Remove the current files at the destination
        if os.path.exists(backup.source_path):
            shutil.rmtree(backup.source_path)

        # Copy the backup files to the original location
        shutil.copytree(backup_path, backup.source_path)

        # Add system log
        log = SystemLog(
            log_type='info',
            message=f"Restore from '{os.path.basename(backup_path)}' completed successfully"
        )

        db.session.add(log)
        db.session.commit()

        flash('Restore completed successfully.')
    except Exception as e:
        log = SystemLog(
            log_type='error',
            message=f"Restore failed: {str(e)}"
        )

        db.session.add(log)
        db.session.commit()

        flash(f'Restore failed: {str(e)}')

    return redirect(url_for('backup.index'))