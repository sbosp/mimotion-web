from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import User, Task, Record
from datetime import datetime, date

admin_bp = Blueprint('admin', __name__)


def is_admin():
    """检查当前用户是否为管理员"""
    # 这里假设level字段为'admin'表示管理员
    return current_user.is_authenticated and current_user.level == 1


def timestamp_to_datetime(timestamp):
    """将时间戳转换为datetime对象"""
    if timestamp and timestamp > 0:
        return datetime.fromtimestamp(timestamp)
    return None


@admin_bp.route('/admin/users')
@login_required
def user_management():
    """用户管理页面"""
    if not is_admin():
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))

    # 获取所有用户
    users = User.query.order_by(User.created_at.desc()).all()

    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')

    # 如果有搜索条件，进行过滤
    if search:
        users = User.query.filter(
            User.username.contains(search) |
            User.email.contains(search)
        ).order_by(User.created_at.desc()).all()

    return render_template('admin/users.html',
                           users=users,
                           search=search)


@admin_bp.route('/admin/user/<int:user_id>')
@login_required
def user_detail(user_id):
    """用户详情页面"""
    if not is_admin():
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(user_id)

    # 处理VIP时间显示
    vip_start_time = timestamp_to_datetime(user.vip_start_time)
    vip_end_time = timestamp_to_datetime(user.vip_end_time)
    now_timestamp = datetime.now().timestamp()

    return render_template('admin/user_detail.html',
                           user=user,
                           vip_start_time=vip_start_time,
                           vip_end_time=vip_end_time,
                           now_timestamp=now_timestamp)


@admin_bp.route('/admin/user/<int:user_id>/toggle_active')
@login_required
def toggle_user_active(user_id):
    """切换用户激活状态"""
    if not is_admin():
        flash('您没有权限执行此操作')
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(user_id)
    # 这里可以根据需要实现用户激活/禁用逻辑
    # 例如：user.is_active = not user.is_active
    flash(f'用户 {user.username} 状态已更新')
    return redirect(url_for('admin.user_management'))


@admin_bp.route('/admin/tasks')
@login_required
def task_management():
    """任务管理页面"""
    if not is_admin():
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))

    # 获取所有任务
    tasks = Task.query.order_by(Task.created_at.desc()).all()

    # 获取查询参数
    search = request.args.get('search', '')
    task_type = request.args.get('task_type', '', type=str)

    # 如果有搜索条件，进行过滤
    if search:
        tasks = Task.query.filter(
            Task.task_value.contains(search)
        ).order_by(Task.created_at.desc()).all()

    # 按任务类型过滤
    if task_type and task_type.isdigit():
        tasks = Task.query.filter(
            Task.task_type == int(task_type)
        ).order_by(Task.created_at.desc()).all()

    # 获取每个任务的成功率统计
    task_stats = []
    for task in tasks:
        # 获取今日执行记录
        today = date.today()
        today_records = Record.query.filter(
            Record.task_id == task.id,
            Record.created_at >= datetime.combine(today, datetime.min.time())
        ).all()

        total_count = len(today_records)
        success_count = len([r for r in today_records if r.status])
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0

        task_stats.append({
            'task': task,
            'total_count': total_count,
            'success_count': success_count,
            'success_rate': round(success_rate, 2)
        })

    return render_template('admin/tasks.html',
                           task_stats=task_stats,
                           search=search,
                           task_type=task_type)


@admin_bp.route('/admin/task-stats')
@login_required
def task_statistics():
    """当日任务执行成功率统计页面"""
    if not is_admin():
        flash('您没有权限访问此页面')
        return redirect(url_for('main.index'))

    # 获取今日日期
    today = date.today()
    start_of_day = datetime.combine(today, datetime.min.time())

    # 获取今日所有执行记录
    today_records = Record.query.filter(
        Record.created_at >= start_of_day
    ).all()

    # 统计总体成功率
    total_count = len(today_records)
    success_count = len([r for r in today_records if r.status])
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0

    # 按任务类型统计
    task_type_stats = {}
    for record in today_records:
        task_type = record.task_type
        if task_type not in task_type_stats:
            task_type_stats[task_type] = {'total': 0, 'success': 0}

        task_type_stats[task_type]['total'] += 1
        if record.status:
            task_type_stats[task_type]['success'] += 1

    # 计算每个任务类型的成功率
    for task_type, stats in task_type_stats.items():
        stats['success_rate'] = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
        stats['success_rate'] = round(stats['success_rate'], 2)

    # 按用户统计
    user_stats = {}
    for record in today_records:
        user_id = record.user_id
        if user_id not in user_stats:
            user_stats[user_id] = {'total': 0, 'success': 0, 'user': User.query.get(user_id)}

        user_stats[user_id]['total'] += 1
        if record.status:
            user_stats[user_id]['success'] += 1

    # 计算每个用户的成功率
    for user_id, stats in user_stats.items():
        stats['success_rate'] = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
        stats['success_rate'] = round(stats['success_rate'], 2)

    return render_template('admin/task_stats.html',
                           total_count=total_count,
                           success_count=success_count,
                           success_rate=round(success_rate, 2),
                           task_type_stats=task_type_stats,
                           user_stats=user_stats,
                           today=today,
                           today_records=today_records)
