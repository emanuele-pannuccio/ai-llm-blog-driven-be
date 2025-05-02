from database import db
from datetime import datetime, timedelta

class Token(db.Model):
    """Tabella per conservare i JWT revocati/invalidi"""
    __tablename__ = 'tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)  # JWT ID
    type = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    revoked_at = db.Column(db.TIMESTAMP, default=None)
    
    # Relazione con l'utente
    user = db.relationship("User", back_populates="tokens", lazy="selectin")