from database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from dataclasses import dataclass

from sqlalchemy import inspect

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255))  # Campo rinominato per password hashed
    name = db.Column(db.String(100))
    img = db.Column(db.String(255), default="https://cdn.vectorstock.com/i/1000v/92/16/default-profile-picture-avatar-user-icon-vector-46389216.jpg")
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    created_at = db.Column(db.TIMESTAMP, default=datetime.now())
    deleted_at = db.Column(db.TIMESTAMP, default=None)
    
    # Relazioni
    role = db.relationship("Role", back_populates="user", lazy="joined")
    posts = db.relationship("Post", back_populates="user")
    comments = db.relationship("Comment", back_populates="user")
    tokens = db.relationship("Token", back_populates="user")
    
    # Metodi per la gestione della password
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def image(self):
        return self.img
    
    @image.setter
    def image(self, image):
        if image is None:
            image = ""
        self.img = image
    
    # def __dict__(self):
    #     return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }