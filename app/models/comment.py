from database import db
from datetime import datetime

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    created_at = db.Column(db.DateTime, default=datetime.now())
    deleted_at = db.Column(db.TIMESTAMP, default=None)
    
    # Relazioni
    user = db.relationship("User", back_populates="comments")
    post = db.relationship("Post", back_populates="comments")
