from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import MiAccount, StepRecord
from app import db
from app.utils.mi_motion import MiMotion
from datetime import datetime, timedelta
import random

account_bp = Blueprint('account', __name__)

@account_bp.route('/accounts')
@login_required
def list_accounts():
    accounts = current_user.accounts.all()
    return render_template('account/list.html', accounts=accounts)

@account_bp.route('/account/add', methods=['GET', 'POST'])
@login_required
def add_account():
    if request.method == 'POST':
        mi_user = request.form.get('mi_user')
        mi_password = request.form.get('mi_password')
        min_step = request.form.get('min_step', 18000)
        max_step = request.form.get('max_step', 25000)
        sync_start_hour = request.form.get('sync_start_hour', 8)
        sync_end_hour = request.form.get('sync_end_hour', 22)
        
        # 验证账号
        try:
            mi_motion = MiMotion(mi_user, mi_password)
            message, status = mi_motion.sync_step(100)  # 测试同步一个小步数
            if not status:
                flash('账号验证失败：' + message)
                return redirect(url_for('account.add_account'))
        except Exception as e:
            flash('账号验证失败：' + str(e))
            return redirect(url_for('account.add_account'))
        
        account = MiAccount(
            owner=current_user,
            mi_user=mi_user,
            mi_password=mi_password,
            min_step=min_step,
            max_step=max_step,
            sync_start_hour=sync_start_hour,
            sync_end_hour=sync_end_hour
        )
        db.session.add(account)
        db.session.commit()
        
        flash('账号添加成功')
        return redirect(url_for('account.list_accounts'))
    
    return render_template('account/add.html')

@account_bp.route('/account/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_account(id):
    account = MiAccount.query.get_or_404(id)
    if account.user_id != current_user.id:
        flash('无权操作此账号')
        return redirect(url_for('account.list_accounts'))
    
    if request.method == 'POST':
        account.min_step = request.form.get('min_step', 18000)
        account.max_step = request.form.get('max_step', 25000)
        account.sync_start_hour = request.form.get('sync_start_hour', 8)
        account.sync_end_hour = request.form.get('sync_end_hour', 22)
        account.is_active = request.form.get('is_active') == 'on'
        db.session.commit()
        
        flash('账号更新成功')
        return redirect(url_for('account.list_accounts'))
    
    return render_template('account/edit.html', account=account)

@account_bp.route('/account/<int:id>/delete')
@login_required
def delete_account(id):
    account = MiAccount.query.get_or_404(id)
    if account.user_id != current_user.id:
        flash('无权操作此账号')
        return redirect(url_for('account.list_accounts'))
    
    db.session.delete(account)
    db.session.commit()
    
    flash('账号删除成功')
    return redirect(url_for('account.list_accounts'))

@account_bp.route('/account/<int:id>/records')
@login_required
def account_records(id):
    account = MiAccount.query.get_or_404(id)
    if account.user_id != current_user.id:
        flash('无权查看此账号记录')
        return redirect(url_for('account.list_accounts'))
    
    # 获取最近7天的记录
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    records = StepRecord.query.filter(
        StepRecord.account_id == id,
        StepRecord.created_at >= start_date,
        StepRecord.created_at <= end_date
    ).order_by(StepRecord.created_at.desc()).all()
    
    return render_template('account/records.html', account=account, records=records)

@account_bp.route('/account/<int:id>/sync')
@login_required
def sync_account(id):
    account = MiAccount.query.get_or_404(id)
    if account.user_id != current_user.id:
        flash('无权操作此账号')
        return redirect(url_for('account.list_accounts'))
    
    try:
        # 获取当前时间对应的步数范围
        hour = datetime.now().hour
        time_rate = min(hour / 22, 1)
        min_step = int(time_rate * account.min_step)
        max_step = int(time_rate * account.max_step)
        step_count = random.randint(min_step, max_step)
        
        # 同步步数
        mi_motion = MiMotion(account.mi_user, account.mi_password)
        message, status = mi_motion.sync_step(step_count)
        
        # 记录结果
        record = StepRecord(
            account_id=account.id,
            step_count=step_count,
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
    
    return redirect(url_for('account.list_accounts'))

@account_bp.route('/api/account/<int:id>/stats')
@login_required
def account_stats(id):
    account = MiAccount.query.get_or_404(id)
    if account.user_id != current_user.id:
        return jsonify({'error': '无权查看此账号数据'}), 403
    
    # 获取最近7天的统计数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    records = StepRecord.query.filter(
        StepRecord.account_id == id,
        StepRecord.created_at >= start_date,
        StepRecord.created_at <= end_date
    ).order_by(StepRecord.created_at.asc()).all()
    
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