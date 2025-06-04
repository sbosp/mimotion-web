from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import MiAccount, StepRecord
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('index.html')
    
    # 获取用户的账号统计信息
    accounts = current_user.accounts.all()
    total_accounts = len(accounts)
    active_accounts = sum(1 for acc in accounts if acc.is_active)
    
    # 获取最近24小时的同步记录
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=24)
    recent_records = StepRecord.query.join(MiAccount).filter(
        MiAccount.user_id == current_user.id,
        StepRecord.created_at >= start_date,
        StepRecord.created_at <= end_date
    ).order_by(StepRecord.created_at.desc()).all()
    
    success_syncs = sum(1 for rec in recent_records if rec.status)
    total_syncs = len(recent_records)
    
    return render_template('dashboard.html',
                         total_accounts=total_accounts,
                         active_accounts=active_accounts,
                         recent_records=recent_records,
                         success_syncs=success_syncs,
                         total_syncs=total_syncs) 