import json

from datetime import datetime
import pytz


def get_current_step_range(hour=None):
    """根据当前时间获取步数范围"""
    if hour is None:
        hour = datetime.now(pytz.timezone('Asia/Shanghai')).hour
    time_rate = min(hour / 22, 1)  # 22点达到最大值
    return lambda task: (
        int(time_rate * task.min_step),
        int(time_rate * task.max_step)
    )


def sync_steps():
    """每小时同步步数"""
    from app import scheduler, db
    from app.models import Task, Record
    from app.utils.mi_motion import MiMotion

    with scheduler.app.app_context():
        # 获取当前小时
        current_hour = datetime.now(pytz.timezone('Asia/Shanghai')).hour
        print(f'当前小时: {current_hour}')
        # 获取所有启用的账号，并且当前时间在其设置的同步时间范围内
        tasks = Task.query.filter(
            Task.is_active == True,
            Task.hour == current_hour
        ).all()

        if not tasks:
            return  # 如果没有需要同步的账号，直接返回
        print('len tasks', len(tasks))
        for task in tasks:
            try:
                # 执行任务
                mi_motion = MiMotion(json.loads(task.task_value))
                message, status = mi_motion.sync_step()

                # 记录结果
                record = Record(
                    task_id=task.id,
                    user_id=task.user_id,
                    task_type=task.task_type,
                    task_params=task.task_value,
                    task_name=json.loads(task.task_value).get('mi_user',''),
                    task_value=mi_motion.step_count,
                    status=status,
                    message=message
                )
                db.session.add(record)
                db.session.commit()

            except Exception as e:
                # 记录失败
                record = Record(
                    task_id=task.id,
                    user_id=task.user_id,
                    task_type=task.task_type,
                    task_params=task.task_value,
                    task_name=json.loads(task.task_value).get('mi_user',''),
                    task_value="0",
                    status=False,
                    message=str(e)
                )
                db.session.add(record)
                db.session.commit()


if __name__ == "__main__":
    # 北京时间
    current_hour = datetime.now(pytz.timezone('Asia/Shanghai')).hour
    print(f'当前小时: {current_hour}')
