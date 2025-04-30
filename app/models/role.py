from database import db

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(50), nullable=False, unique=True)
    user = db.relationship("User", back_populates="role", lazy="selectin", uselist=True)
