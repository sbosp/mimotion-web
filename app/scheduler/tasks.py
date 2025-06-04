from app import scheduler, db
from app.models import MiAccount, StepRecord
from app.utils.mi_motion import MiMotion
import random
from datetime import datetime
import pytz

def get_current_step_range(hour=None):
    """根据当前时间获取步数范围"""
    if hour is None:
        hour = datetime.now(pytz.timezone('Asia/Shanghai')).hour
    time_rate = min(hour / 22, 1)  # 22点达到最大值
    return lambda account: (
        int(time_rate * account.min_step), 
        int(time_rate * account.max_step)
    )

@scheduler.task('cron', id='sync_steps', hour='*')
def sync_steps():
    """每小时同步步数"""
    with scheduler.app.app_context():
        # 获取当前小时
        current_hour = datetime.now(pytz.timezone('Asia/Shanghai')).hour
        
        # 获取所有启用的账号，并且当前时间在其设置的同步时间范围内
        accounts = MiAccount.query.filter(
            MiAccount.is_active == True,
            MiAccount.sync_start_hour <= current_hour,
            MiAccount.sync_end_hour >= current_hour
        ).all()
        
        if not accounts:
            return  # 如果没有需要同步的账号，直接返回
        
        get_range = get_current_step_range(current_hour)
        
        for account in accounts:
            try:
                # 获取当前时间对应的步数范围
                min_step, max_step = get_range(account)
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
                
            except Exception as e:
                # 记录失败
                record = StepRecord(
                    account_id=account.id,
                    step_count=0,
                    status=False,
                    message=str(e)
                )
                db.session.add(record)
                db.session.commit() 