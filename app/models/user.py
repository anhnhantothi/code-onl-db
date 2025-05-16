from ..extensions import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False) 

    certificate = db.relationship('Certificate', back_populates='user')
    user_info = db.relationship('UserInfo', back_populates='user')
    practice_processes = db.relationship('PracticeProcess', back_populates='user')
