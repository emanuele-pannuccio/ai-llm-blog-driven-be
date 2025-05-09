from database import db

from models.post_rel import post_tags

class Tag(db.Model):
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(50), nullable=False, unique=True)
    
    posts = db.relationship("Post", secondary=post_tags, back_populates="tags", lazy="selectin")
