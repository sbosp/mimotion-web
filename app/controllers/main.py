from flask import Blueprint, render_template, Response
from flask_login import login_required, current_user
from app.models import Task, Record
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('index.html')
    # 获取用户的账号统计信息
    tasks = current_user.tasks.all()
    total_tasks = len(tasks)
    active_tasks = sum(1 for task in tasks if task.is_active)

    # 获取最近24小时的同步记录
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=24)
    recent_records = Record.query.join(Task).filter(
        Task.user_id == current_user.id,
        Record.created_at >= start_date,
        Record.created_at <= end_date
    ).order_by(Record.created_at.desc()).all()

    success_syncs = sum(1 for rec in recent_records if rec.status)
    total_syncs = len(recent_records)
    return render_template('dashboard.html',
                           total_tasks=total_tasks,
                           active_tasks=active_tasks,
                           recent_records=recent_records,
                           success_syncs=success_syncs,
                           total_syncs=total_syncs)


@main_bp.route('/ads.text')
def gad():
    content = """google.com, pub-1234567890123456, DIRECT, f08c47fec0942fa0"""
    return Response(content, mimetype='text/plain')