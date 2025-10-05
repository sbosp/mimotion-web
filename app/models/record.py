import pytz

from app import db
from datetime import datetime


class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    task_type = db.Column(db.Integer, default=1)
    task_params = db.Column(db.String(), default='')
    task_name = db.Column(db.String(), default='')
    task_value = db.Column(db.String(), default='')  # 步数
    status = db.Column(db.Boolean, default=True)  # 是否成功
    message = db.Column(db.String(255))  # 执行结果消息
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Shanghai')))

    def __repr__(self):
        return f'<Record {self.task_value}>'
