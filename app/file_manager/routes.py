# app/file_manager/routes.py
import os
from flask import render_template, redirect, url_for, flash, request, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.file_manager import bp
from app.models import File
from app.file_manager.forms import UploadFileForm, CreateFolderForm
from app.decorators import permission_required


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'gif', 'csv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    path = request.args.get('path', '')

    # Root directory handling
    if not path:
        # Both admin and regular users see these root directories
        if current_user.role == 'admin':
            directories = [
                {'name': 'shared', 'is_dir': True, 'size': 0, 'modified': 0},
                {'name': 'users', 'is_dir': True, 'size': 0, 'modified': 0}
            ]
        else:
            # Regular users see shared and their own directory
            directories = [
                {'name': 'shared', 'is_dir': True, 'size': 0, 'modified': 0},
                {'name': 'my files', 'is_dir': True, 'size': 0, 'modified': 0}
            ]
        return render_template('file_manager/index.html',
                               files=directories,
                               current_path='',
                               parent_path='',
                               upload_form=UploadFileForm(),
                               folder_form=CreateFolderForm())

    # Handle virtual path 'my files' for regular users
    if (path == 'my files' or path.startswith('my files/')) and current_user.role != 'admin':
        path = path.replace('my files', f'users/{current_user.username}', 1)

    # Security checks (strict only for non-admin users)
    path_parts = path.split('/')
    if current_user.role != 'admin':
        if path_parts and path_parts[0] not in ['shared', 'users', '']:
            flash('Access denied.')
            return redirect(url_for('file_manager.index'))

        if path_parts and path_parts[0] == 'users':
            if len(path_parts) < 2 or path_parts[1] != current_user.username:
                flash('Access denied.')
                return redirect(url_for('file_manager.index'))

    # Ensure path is properly formatted (no double slashes, etc.)
    path = path.strip('/').replace('//', '/')
    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], path)

    # Create directory if it doesn't exist
    if not os.path.exists(full_path):
        try:
            os.makedirs(full_path)
            print(f"Created directory: {full_path}")
        except Exception as e:
            print(f"Error creating directory: {str(e)}")
            flash('Path does not exist and could not be created.')
            return redirect(url_for('file_manager.index'))

    # Calculate parent path
    if current_user.role != 'admin' and path.startswith(f'users/{current_user.username}'):
        # For regular users viewing their own directory
        parts = path.split('/')
        if len(parts) <= 2:  # at users/username level
            parent_path = ''  # Root level
        else:
            # Remove the first two components (users/username) and join the rest
            parent_path = 'my files/' + '/'.join(parts[2:len(parts) - 1])
    else:
        # For admin users, use normal path handling
        parent_path = os.path.dirname(path)

    # List files in the directory
    files = []
    try:
        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)
            is_dir = os.path.isdir(item_path)
            try:
                size = os.path.getsize(item_path) if not is_dir else 0
                modified = os.path.getmtime(item_path)
            except OSError:
                size = 0
                modified = 0

            files.append({
                'name': item,
                'is_dir': is_dir,
                'size': size,
                'modified': modified
            })
    except Exception as e:
        print(f"Error listing directory {full_path}: {str(e)}")
        flash(f"Error accessing directory: {str(e)}")
        return redirect(url_for('file_manager.index'))

    # For regular users, if we're showing their home directory, display it as "my files"
    display_path = path
    if current_user.role != 'admin' and path.startswith(f'users/{current_user.username}'):
        display_path = 'my files' + path[len(f'users/{current_user.username}'):]

    upload_form = UploadFileForm()
    folder_form = CreateFolderForm()

    return render_template('file_manager/index.html',
                           files=files,
                           current_path=display_path,
                           parent_path=parent_path,
                           upload_form=upload_form,
                           folder_form=folder_form)


@bp.route('/upload', methods=['POST'])
@login_required
@permission_required('write')
def upload_file():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data

        # Get the display path from the form
        display_path = request.form.get('path', '')
        print(f"Upload file - Display path: {display_path}")

        # Convert display path to actual filesystem path
        actual_path = display_path
        if (display_path == 'my files' or display_path.startswith('my files/')) and current_user.role != 'admin':
            actual_path = display_path.replace('my files', f'users/{current_user.username}', 1)

        print(f"Upload file - Actual path: {actual_path}")

        # Security check
        if current_user.role != 'admin':
            path_parts = actual_path.split('/')
            if path_parts and path_parts[0] not in ['shared', 'users', '']:
                flash('Access denied.')
                return redirect(url_for('file_manager.index'))

            if path_parts and path_parts[0] == 'users':
                if len(path_parts) < 2 or path_parts[1] != current_user.username:
                    flash('Access denied.')
                    return redirect(url_for('file_manager.index'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], actual_path)

            print(f"Saving file to: {save_path}")

            if not os.path.exists(save_path):
                os.makedirs(save_path)

            file_path = os.path.join(save_path, filename)
            file.save(file_path)

            # Save file metadata to database
            file_size = os.path.getsize(file_path)
            file_type = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

            # Use actual_path for database filepath
            db_file = File(
                filename=filename,
                filepath=os.path.join(actual_path, filename),
                filetype=file_type,
                filesize=file_size,
                user_id=current_user.id
            )

            db.session.add(db_file)
            db.session.commit()

            flash(f'File {filename} uploaded successfully.')
        else:
            flash('File type not allowed.')

    # Redirect to the display path
    return redirect(url_for('file_manager.index', path=display_path))


@bp.route('/download/<path:filepath>')
@login_required
def download_file(filepath):
    # Security check - prevent users from accessing unauthorized paths
    path_parts = filepath.split('/')
    if path_parts and path_parts[0] not in ['shared', 'users']:
        flash('Access denied.')
        return redirect(url_for('file_manager.index'))

    # Additional check for non-admins trying to access other users' folders
    if current_user.role != 'admin' and path_parts and path_parts[0] == 'users':
        if len(path_parts) < 2 or path_parts[1] != current_user.username:
            flash('Access denied.')
            return redirect(url_for('file_manager.index'))

    directory = os.path.dirname(os.path.join(current_app.config['UPLOAD_FOLDER'], filepath))
    filename = os.path.basename(filepath)
    return send_from_directory(directory, filename, as_attachment=True)


@bp.route('/delete/<path:filepath>')
@login_required
def delete_file(filepath):
    # Security check - prevent users from accessing unauthorized paths
    path_parts = filepath.split('/')
    if path_parts and path_parts[0] not in ['shared', 'users']:
        flash('Access denied.')
        return redirect(url_for('file_manager.index'))

    # Additional check for non-admins trying to access other users' folders
    if current_user.role != 'admin' and path_parts and path_parts[0] == 'users':
        if len(path_parts) < 2 or path_parts[1] != current_user.username:
            flash('Access denied.')
            return redirect(url_for('file_manager.index'))

    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filepath)

    if not os.path.exists(full_path):
        flash('File not found.')
        return redirect(url_for('file_manager.index'))

    # Check if it's a file or directory
    if os.path.isfile(full_path):
        os.remove(full_path)

        # Remove from database
        file = File.query.filter_by(filepath=filepath).first()
        if file:
            db.session.delete(file)
            db.session.commit()

        flash('File deleted successfully.')
    else:
        # For simplicity, only allow deleting empty directories
        try:
            os.rmdir(full_path)
            flash('Directory deleted successfully.')
        except OSError:
            flash('Directory is not empty.')

    parent_dir = os.path.dirname(filepath)
    return redirect(url_for('file_manager.index', path=parent_dir))


@bp.route('/create_folder', methods=['POST'])
@login_required
def create_folder():
    # Get the display path from the form
    display_path = request.form.get('path', '')

    # Print debug info
    print(f"Create folder - Display path: {display_path}")

    # Convert display path to actual filesystem path
    actual_path = display_path
    if (display_path == 'my files' or display_path.startswith('my files/')) and current_user.role != 'admin':
        actual_path = display_path.replace('my files', f'users/{current_user.username}', 1)

    # Print more debug info
    print(f"Create folder - Actual path: {actual_path}")

    # Security check
    if current_user.role != 'admin':
        path_parts = actual_path.split('/')
        if path_parts and path_parts[0] not in ['shared', 'users', '']:
            flash('Access denied.')
            return redirect(url_for('file_manager.index'))

        if path_parts and path_parts[0] == 'users':
            if len(path_parts) < 2 or path_parts[1] != current_user.username:
                flash('Access denied.')
                return redirect(url_for('file_manager.index'))

    form = CreateFolderForm()
    if form.validate_on_submit():
        folder_name = secure_filename(form.folder_name.data)

        # Important fix: For admin, make sure we're using the current path, not root
        folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], actual_path, folder_name)
        print(f"Creating folder at: {folder_path}")

        if os.path.exists(folder_path):
            flash('Folder already exists.')
        else:
            try:
                os.makedirs(folder_path)
                print(f"Folder created successfully at: {folder_path}")
                flash(f'Folder {folder_name} created successfully.')
            except Exception as e:
                print(f"Error creating folder: {str(e)}")
                flash(f'Error creating folder: {str(e)}')

    # Redirect to the display path (what the user sees)
    return redirect(url_for('file_manager.index', path=display_path))


@bp.route('/rename', methods=['POST'])
@login_required
def rename():
    path = request.form.get('path', '')

    # Security check - prevent users from accessing unauthorized paths
    path_parts = path.split('/')
    if path_parts and path_parts[0] not in ['shared', 'users', '']:
        flash('Access denied.')
        return redirect(url_for('file_manager.index'))

    # Additional check for non-admins trying to access other users' folders
    if current_user.role != 'admin' and path_parts and path_parts[0] == 'users':
        if len(path_parts) < 2 or path_parts[1] != current_user.username:
            flash('Access denied.')
            return redirect(url_for('file_manager.index'))

    # Handle "my files" virtual directory for regular users
    if path.startswith('my files') and current_user.role != 'admin':
        path = f'users/{current_user.username}' + path[8:]  # Replace 'my files' with 'users/username'

    old_name = request.form.get('old_name')
    new_name = secure_filename(request.form.get('new_name'))

    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], path, old_name)
    new_path = os.path.join(current_app.config['UPLOAD_FOLDER'], path, new_name)

    if not os.path.exists(old_path):
        flash('File or folder not found.')
    elif os.path.exists(new_path):
        flash('A file or folder with that name already exists.')
    else:
        os.rename(old_path, new_path)

        # Update database record if it's a file
        if os.path.isfile(new_path):
            file = File.query.filter_by(filepath=os.path.join(path, old_name)).first()
            if file:
                file.filename = new_name
                file.filepath = os.path.join(path, new_name)
                db.session.commit()

        flash('Renamed successfully.')

    # If the path contains 'users/username' for regular users, convert back to 'my files'
    display_path = path
    if current_user.role != 'admin' and path.startswith(f'users/{current_user.username}'):
        display_path = 'my files' + path[len(f'users/{current_user.username}'):]

    return redirect(url_for('file_manager.index', path=display_path))