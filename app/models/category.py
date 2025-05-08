from database import db

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(260), nullable=False)
    
    posts = db.relationship("Post", back_populates="category", lazy="selectin")
