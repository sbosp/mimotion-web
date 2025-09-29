import json

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import Task, Record
from app import db
from app.utils.mi_motion import MiMotion
from datetime import datetime, timedelta
import random

task_bp = Blueprint('task', __name__)


@task_bp.route('/tasks')
@login_required
def list_tasks():
    tasks = current_user.tasks.all()
    parsed_tasks = []
    for task in tasks:
        task.parsed_task_value = json.loads(task.task_value)
        parsed_tasks.append(task)
    return render_template('task/list.html', tasks=parsed_tasks)


@task_bp.route('/task/add', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST':
        mi_user = request.form.get('mi_user')
        mi_password = request.form.get('mi_password')
        min_step = request.form.get('min_step', 6666)
        max_step = request.form.get('max_step', 9999)
        sync_start_hour = request.form.get('sync_start_hour', 8)
        # sync_end_hour = request.form.get('sync_end_hour', 22)

        # 验证账号
        try:
            mi_motion = MiMotion(task_value={
                'mi_user': mi_user,
                'mi_password': mi_password,
                'min_step': 100,
                'max_step': 200,
            })
            message, status = mi_motion.sync_step()  # 测试同步一个小步数
            if not status:
                flash('账号验证失败：' + message)
                return redirect(url_for('task.add_task'))
        except Exception as e:
            flash('账号验证失败：' + str(e))
            return redirect(url_for('task.add_task'))

        task_value = {
            'mi_user': mi_user,
            'mi_password': mi_password,
            'min_step': min(min_step, max_step),
            'max_step': max(min_step, max_step),
        }
        task = Task(
            owner=current_user,
            task_type=1,
            task_value=json.dumps(task_value),
            day=1,
            hour=sync_start_hour,
        )
        db.session.add(task)
        db.session.commit()

        flash('账号添加成功')
        return redirect(url_for('task.list_tasks'))

    return render_template('task/add.html')


@task_bp.route('/task/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        flash('无权操作此账号')
        return redirect(url_for('task.list_tasks'))

    if request.method == 'POST':
        min_step = request.form.get('min_step', 6666)
        max_step = request.form.get('max_step', 9999)
        value = json.loads(task.task_value)
        task_value = {
            'mi_user': value.mi_user,
            'mi_password': value.mi_password,
            'min_step': min(min_step, max_step),
            'max_step': max(min_step, max_step),
        }
        task.task_value = json.dumps(task_value)
        task.day = 1
        task.hour = request.form.get('sync_start_hour', 8)
        # task.sync_end_hour = request.form.get('sync_end_hour', 22)
        task.is_active = request.form.get('is_active') == 'on'
        db.session.commit()

        flash('账号更新成功')
        return redirect(url_for('task.list_tasks'))
    print(task.hour)
    return render_template('task/edit.html', task=task, task_value=json.loads(task.task_value))


@task_bp.route('/task/<int:id>/delete')
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        flash('无权操作此账号')
        return redirect(url_for('task.list_tasks'))

    db.session.delete(task)
    db.session.commit()

    flash('账号删除成功')
    return redirect(url_for('task.list_tasks'))


@task_bp.route('/task/<int:id>/records')
@login_required
def task_records(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        flash('无权查看此账号记录')
        return redirect(url_for('task.list_tasks'))

    # 获取最近7天的记录
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    records = Record.query.filter(
        Record.task_id == id,
        Record.created_at >= start_date,
        Record.created_at <= end_date
    ).order_by(Record.created_at.desc()).all()

    return render_template('task/records.html', task=task, task_value=json.loads(task.task_value), records=records)


@task_bp.route('/task/<int:id>/sync')
@login_required
def sync_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        flash('无权操作此账号')
        return redirect(url_for('task.list_tasks'))

    try:
        # 同步步数
        mi_motion = MiMotion(json.loads(task.task_value))
        message, status = mi_motion.sync_step()

        # 记录结果
        record = Record(
            task_id=task.id,
            user_id=task.user_id,
            task_type=1,
            task_params=task.task_value,
            task_name=json.loads(task.task_value).get('mi_user',''),
            task_value=str(mi_motion.step_count),
            status=status,
            message=message
        )
        db.session.add(record)
        db.session.commit()

        if status:
            flash('同步成功：' + message)
        else:
            flash('同步失败：' + message)

    except Exception as e:
        flash('同步失败：' + str(e))

    return redirect(url_for('task.list_tasks'))


@task_bp.route('/api/task/<int:id>/stats')
@login_required
def task_stats(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        return jsonify({'error': '无权查看此账号数据'}), 403

    # 获取最近7天的统计数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    records = Record.query.filter(
        Record.task_id == id,
        Record.created_at >= start_date,
        Record.created_at <= end_date
    ).order_by(Record.created_at.asc()).all()

    dates = []
    steps = []
    success_rate = []

    for record in records:
        dates.append(record.created_at.strftime('%Y-%m-%d'))
        steps.append(record.step_count)
        success_rate.append(1 if record.status else 0)

    return jsonify({
        'dates': dates,
        'steps': steps,
        'success_rate': success_rate
    })
