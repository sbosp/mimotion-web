from app import db
from datetime import datetime

class MiAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    mi_user = db.Column(db.String(120), nullable=False)  # 小米运动账号
    mi_password = db.Column(db.String(120), nullable=False)  # 小米运动密码
    min_step = db.Column(db.Integer, default=18000)  # 最小步数
    max_step = db.Column(db.Integer, default=25000)  # 最大步数
    is_active = db.Column(db.Boolean, default=True)  # 是否启用
    sync_start_hour = db.Column(db.Integer, default=8)  # 同步开始时间（小时）
    sync_end_hour = db.Column(db.Integer, default=22)  # 同步结束时间（小时）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联步数记录
    step_records = db.relationship('StepRecord', backref='account', lazy='dynamic')
    
    def __repr__(self):
        return f'<MiAccount {self.mi_user}>' 