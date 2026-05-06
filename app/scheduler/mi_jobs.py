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
    import app.utils.mi_utils as mitask
    import time
    
    with scheduler.app.app_context():
        # 获取当前小时
        current_hour = datetime.now(pytz.timezone('Asia/Shanghai')).hour
        print(f'[sync_steps] 开始执行同步任务，当前小时: {current_hour}')
        
        # 获取所有启用的账号，并且当前时间在其设置的同步时间范围内
        tasks = Task.query.filter(
            Task.is_active == True,
            Task.hour == current_hour
        ).all()

        if not tasks:
            print('[sync_steps] 没有需要同步的任务')
            return  # 如果没有需要同步的账号，直接返回
            
        print(f'[sync_steps] 需要同步的任务数量: {len(tasks)}')
        
        # 批量处理任务，减少数据库操作
        records_to_add = []
        total_start_time = time.time()
        success_count = 0
        fail_count = 0
        
        for i, task in enumerate(tasks):
            try:
                # 设置超时时间，避免单个任务执行时间过长
                task_start_time = time.time()
                timeout = 180  # 3分钟超时（减少超时时间）
                
                print(f'[sync_steps] 开始执行任务 {i+1}/{len(tasks)} (ID: {task.id})')
                
                # 执行任务
                task_value, status, message, step_count = mitask.run(json.loads(task.task_value))
                
                task_execution_time = time.time() - task_start_time
                
                # 检查是否超时
                if task_execution_time > timeout:
                    print(f'[sync_steps] 任务 {task.id} 执行超时，耗时: {task_execution_time:.2f}秒')
                    status = False
                    message = f'任务执行超时 ({task_execution_time:.2f}秒)'
                    step_count = 0
                else:
                    print(f'[sync_steps] 任务 {task.id} 执行完成，耗时: {task_execution_time:.2f}秒，状态: {status}')

                # 记录结果
                record = Record(
                    task_id=task.id,
                    user_id=task.user_id,
                    task_type=task.task_type,
                    task_params=json.dumps(task_value),
                    task_name=task_value.get('mi_user', ''),
                    task_value=str(step_count),
                    status=status,
                    message=message
                )
                task.task_value = json.dumps(task_value)
                records_to_add.append(record)
                
                if status:
                    success_count += 1
                else:
                    fail_count += 1

            except Exception as e:
                # 记录失败
                record = Record(
                    task_id=task.id,
                    user_id=task.user_id,
                    task_type=task.task_type,
                    task_params=task.task_value,
                    task_name=json.loads(task.task_value).get('mi_user', ''),
                    task_value="0",
                    status=False,
                    message=str(e)
                )
                records_to_add.append(record)
                fail_count += 1
                print(f'[sync_steps] 任务 {task.id} 执行失败: {e}')
        
        # 批量提交数据库操作
        if records_to_add:
            try:
                db.session.add_all(records_to_add)
                db.session.commit()
                total_execution_time = time.time() - total_start_time
                print(f'[sync_steps] 批量提交 {len(records_to_add)} 条记录成功，总耗时: {total_execution_time:.2f}秒，成功: {success_count}, 失败: {fail_count}')
            except Exception as e:
                db.session.rollback()
                print(f'[sync_steps] 批量提交失败: {e}')
        else:
            print('[sync_steps] 没有需要提交的记录')


if __name__ == "__main__":
    # 北京时间
    current_hour = datetime.now(pytz.timezone('Asia/Shanghai')).hour
    print(f'当前小时: {current_hour}')
