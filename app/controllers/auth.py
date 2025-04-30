from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, current_user, get_jti, unset_jwt_cookies

from datetime import datetime

from database import db
from models.token import Token
from models.user import User

from config import Config

class AuthService:
    @staticmethod
    def createToken(user_data):
        """Crea un nuovo utente con password hashata"""
        # Verifica se l'utente esiste già
        user : User = User.query.filter(User.email == user_data['email']).one_or_none()

        if user is None or not user.verify_password(user_data["password"]):
            raise ValueError("Wrong email or password")
        
        access_token = AuthService.createAccessToken(user)
        refresh_token = AuthService.createRefreshToken(user)

        return {"access_token": access_token, "refresh_token": refresh_token}
    
    @staticmethod
    def createAccessToken(user):
        AuthService.revokeOldAccessToken(user)

        access_token = create_access_token(identity=str(user.id), expires_delta=Config.JWT_ACCESS_TOKEN_EXPIRES)
        access_token_db_rec = Token(jti=get_jti(access_token), type="ACCESS", user_id=user.id)
        db.session.add(access_token_db_rec)
        db.session.commit()

        return access_token
    
    @staticmethod
    def revokeOldAccessToken(user):
        old_access_token : Token = Token.query.filter(Token.revoked_at == None,Token.user_id == user.id,Token.type == "ACCESS").one_or_none()

        if old_access_token is not None:
            old_access_token.revoked_at = datetime.now()
            db.session.commit()

    @staticmethod
    def createRefreshToken(user):
        AuthService.revokeOldRefreshToken(user)

        refresh_token = create_refresh_token(identity=str(user.id))
        refresh_token_db_rec = Token(jti=get_jti(refresh_token), type="REFRESH", user_id=user.id)
        db.session.add(refresh_token_db_rec)
        db.session.commit()

        return refresh_token

    @staticmethod
    def revokeOldRefreshToken(user):
        old_refr_token : Token = Token.query.filter(Token.revoked_at == None,Token.user_id == user.id,Token.type == "REFRESH").one_or_none()

        if old_refr_token is not None:
            old_refr_token.revoked_at = datetime.now()
            db.session.commit()

    @staticmethod
    def refreshAccessToken(user):
        """Crea un nuovo utente con password hashata"""
        # Verifica se l'utente esiste già
        print(user)

        access_token = AuthService.createAccessToken(user)

        return {"access_token": access_token}
    
    @staticmethod
    def logout(user):
        AuthService.revokeOldAccessToken(user)
        AuthService.revokeOldRefreshToken(user)

        return {"ok" : 1}

    @staticmethod
    def findToken(jti):
        return Token.query.filter(Token.jti == jti, Token.revoked_at == None).one_or_none()

    @staticmethod
    def checkRevokedToken(jti):
        return AuthService.findToken(jti) is None