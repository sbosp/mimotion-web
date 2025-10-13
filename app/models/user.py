from app import db
from datetime import datetime
import pytz
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    level = db.Column(db.Integer, default=0)
    password = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))
    vip_type = db.Column(db.Integer, default=0)
    vip_start_time = db.Column(db.BigInteger, default=0)
    vip_end_time = db.Column(db.BigInteger, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Shanghai')))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Shanghai')), onupdate=lambda: datetime.now(pytz.timezone('Asia/Shanghai')))

    # 关联账号
    tasks = db.relationship('Task', backref='owner', lazy='dynamic')

    def set_password(self, password):
        self.password = password
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
