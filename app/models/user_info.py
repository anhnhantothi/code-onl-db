# app/models/user_info.py
from ..extensions import db
from datetime import datetime

class UserInfo(db.Model):
    __tablename__ = 'user_info'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

    code = db.Column(db.String(50), nullable=False, unique=True)
    gender = db.Column(db.Enum('MALE', 'FEMALE', name='gender_enum'), nullable=False)
    job = db.Column(db.String(255))
    full_name = db.Column(db.String(255))
    phone_number = db.Column(db.String(20))
    address = db.Column(db.String(255))
    start_date = db.Column(db.DateTime, nullable=True)
    last_online = db.Column(db.DateTime, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    vip = db.Column(db.Boolean, default=False)
    enabled = db.Column(db.Boolean, default=True)

    user = db.relationship('User', back_populates='user_info')
