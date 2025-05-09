from database import db

class PostStatus(db.Model):
    __tablename__ = 'post_status'
    
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), nullable=False, unique=True)
    posts = db.relationship("Post", back_populates="status", lazy="selectin")
