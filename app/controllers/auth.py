from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, current_user, get_jti, unset_jwt_cookies, get_jwt

import json

from datetime import datetime
from zoneinfo import ZoneInfo

from database import db
from models.token import Token
from models.user import User

from config import Config

class AuthService:
    @staticmethod
    def createToken(user_data):
        """Verifica le credenziali e genera access e refresh token."""
        user = User.query.filter_by(email=user_data['email']).one_or_none()

        if not user or not user.verify_password(user_data["password"]):
            raise ValueError("Wrong email or password")
        
        refresh_token = AuthService.createRefreshToken(user)
        access_token = AuthService.createAccessToken(user, get_jti(refresh_token))

        return {"access_token": access_token, "refresh_token": refresh_token}
    
    @staticmethod
    def refresh_from_token(jwt_payload):
        jti = jwt_payload["jti"]

        if AuthService.is_token_revoked(jti):
            raise ValueError("Refresh token is revoked")

        user_id = int(jwt_payload["sub"])
        user = User.query.get(user_id)

        # Crea nuovo access token
        access_token = AuthService.createAccessToken(user, jti)

        return {"access_token": access_token}
    
    @staticmethod
    def createAccessToken(user, refresh_token):
        return create_access_token(
            identity=str(user.id),
            expires_delta=Config.JWT_ACCESS_TOKEN_EXPIRES,
            additional_claims={
                "refresh_token" : refresh_token
            }
        )

    @staticmethod
    def createRefreshToken(user):
        return create_refresh_token(
            identity=str(user.id),
            expires_delta=Config.JWT_REFRESH_TOKEN_EXPIRES
        )

    @staticmethod
    def logout_tokens(jwt_payload):
        """Revoca i token presenti nella richiesta JWT."""
        jti = jwt_payload["jti"]
        token_type = jwt_payload["type"]
        user_id = jwt_payload["sub"]

        revoked_jwt = Token(
            jti=jti,
            type=token_type.upper(),
            user_id=int(user_id),
            revoked_at=datetime.now(ZoneInfo("Europe/Rome"))
        )

        revoked_refresh_jwt = Token(
            jti=jwt_payload["refresh_token"],
            type="REFRESH",
            user_id=int(user_id),
            revoked_at=datetime.now(ZoneInfo("Europe/Rome"))
        )

        db.session.add(revoked_jwt)
        db.session.add(revoked_refresh_jwt)
        db.session.commit()

        return {"msg": f"{token_type.capitalize()} token revoked."}

    @staticmethod
    def is_token_revoked(jti):
        """Controlla se il token è stato revocato (blacklistato)."""
        return db.session.query(
            db.exists().where(Token.jti == jti)
        ).scalar()

    @staticmethod
    def findToken(jti):
        """Recupera il token solo se è stato blacklistato."""
        return Token.query.filter_by(jti=jti).one_or_none()

    @staticmethod
    def refreshAccessToken(user):
        access_token = AuthService.createAccessToken(user)
        return {"access_token": access_token}