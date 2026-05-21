# app/system_monitor/routes.py
import os
import psutil
import datetime
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.system_monitor import bp
from app.models import SystemLog
from app import db


@bp.route('/')
@login_required
def index():
    if current_user.role != 'admin':
        flash('Unauthorized access.')
        return redirect(url_for('file_manager.index'))

    # Get system stats
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    # Get latest system logs
    logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).limit(20).all()

    return render_template('system_monitor/index.html',
                           cpu_percent=cpu_percent,
                           memory=memory,
                           disk=disk,
                           logs=logs)


@bp.route('/api/stats')
@login_required
def get_stats():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized access'}), 403

    # Get real-time stats for AJAX updates
    stats = {
        'cpu': {
            'percent': psutil.cpu_percent(interval=1),
            'cores': psutil.cpu_count(),
        },
        'memory': {
            'total': psutil.virtual_memory().total,
            'used': psutil.virtual_memory().used,
            'percent': psutil.virtual_memory().percent
        },
        'disk': {
            'total': psutil.disk_usage('/').total,
            'used': psutil.disk_usage('/').used,
            'percent': psutil.disk_usage('/').percent
        },
        'network': {
            'bytes_sent': psutil.net_io_counters().bytes_sent,
            'bytes_recv': psutil.net_io_counters().bytes_recv
        },
        'time': datetime.datetime.now().strftime('%H:%M:%S')
    }

    return jsonify(stats)


@bp.route('/logs')
@login_required
def logs():
    if current_user.role != 'admin':
        flash('Unauthorized access.')
        return redirect(url_for('file_manager.index'))

    page = request.args.get('page', 1, type=int)
    logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).paginate(
        page=page, per_page=50)

    return render_template('system_monitor/logs.html', logs=logs)


@bp.route('/logs/clear')
@login_required
def clear_logs():
    if current_user.role != 'admin':
        flash('Unauthorized access.')
        return redirect(url_for('file_manager.index'))

    # Delete all logs from the database
    SystemLog.query.delete()
    db.session.commit()

    flash('System logs cleared successfully.')
    return redirect(url_for('system_monitor.logs'))