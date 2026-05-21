# app/user_manager/routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.user_manager import bp
from app.models import User
from app.user_manager.forms import UserForm, EditUserForm
import os
from flask import current_app
from app.models import SystemLog


@bp.route('/')
@login_required
def index():
    # Only admin users can access user management
    if current_user.role != 'admin':
        flash('Unauthorized access.')
        return redirect(url_for('file_manager.index'))

    users = User.query.all()
    return render_template('user_manager/index.html', users=users)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_user():
    if current_user.role != 'admin':
        flash('Unauthorized access.')
        return redirect(url_for('file_manager.index'))

    form = UserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data,
            permissions=','.join(form.permissions.data)
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        # Create user directory
        try:
            # Make sure the users directory exists
            users_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'users')
            if not os.path.exists(users_dir):
                os.makedirs(users_dir)

            # Create the specific user directory
            user_dir = os.path.join(users_dir, user.username)
            if not os.path.exists(user_dir):
                os.makedirs(user_dir)

            # Add a system log entry
            log = SystemLog(
                log_type='info',
                message=f"Created directory for user: {user.username}"
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            flash(f'User created but could not create user directory: {str(e)}')
            # Log the error
            error_log = SystemLog(
                log_type='error',
                message=f"Failed to create directory for user {user.username}: {str(e)}"
            )
            db.session.add(error_log)
            db.session.commit()

        flash(f'User {form.username.data} created successfully.')
        return redirect(url_for('user_manager.index'))

    return render_template('user_manager/create.html', form=form)


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if current_user.role != 'admin':
        flash('Unauthorized access.')
        return redirect(url_for('file_manager.index'))

    user = User.query.get_or_404(id)
    form = EditUserForm()

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        user.permissions = ','.join(form.permissions.data)

        if form.password.data:
            user.set_password(form.password.data)

        db.session.commit()
        flash('User updated successfully.')
        return redirect(url_for('user_manager.index'))
    elif request.method == 'GET':
        form.id.data = str(user.id)
        form.username.data = user.username
        form.email.data = user.email
        form.role.data = user.role

        # Debug print
        print(f"User permissions: {user.permissions}")
        print(f"Permissions type: {type(user.permissions)}")

        form.permissions.data = user.permissions.split(',') if user.permissions else []

    return render_template('user_manager/edit.html', form=form, user=user)


@bp.route('/delete/<int:id>')
@login_required
def delete_user(id):
    if current_user.role != 'admin':
        flash('Unauthorized access.')
        return redirect(url_for('file_manager.index'))

    user = User.query.get_or_404(id)

    # Don't allow deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account.')
        return redirect(url_for('user_manager.index'))

    db.session.delete(user)
    db.session.commit()

    flash('User deleted successfully.')
    return redirect(url_for('user_manager.index'))