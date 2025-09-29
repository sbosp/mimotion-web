from app import db
from datetime import datetime

'''
task_type 1:zepp
'''
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    task_type = db.Column(db.Integer, default=1)
    task_value = db.Column(db.String(), nullable=False)
    is_active = db.Column(db.Boolean, default=True)  # 是否启用
    month = db.Column(db.Integer, default=0)
    week = db.Column(db.Integer, default=0)
    day = db.Column(db.Integer, default=0)
    hour = db.Column(db.Integer, default=0)
    minute = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联任务执行流水记录
    records = db.relationship('Record', backref='task', lazy='dynamic')
    
    def __repr__(self):
        return f'<Task {self.task_value}>'