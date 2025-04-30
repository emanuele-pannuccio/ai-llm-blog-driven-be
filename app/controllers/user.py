from werkzeug.security import generate_password_hash
from sqlalchemy import or_
from datetime import datetime

from database import db
from models.user import User
from models.role import Role

class UserService:
    @staticmethod
    def create_user(user_data):
        """Crea un nuovo utente con password hashata"""
        # Verifica se l'utente esiste già
        print(user_data)
        if User.query.filter(User.email == user_data['email']).first():
            raise ValueError("Username or email already exists")
        
        user = User(**user_data)
        user.role_id = Role.query.filter(Role.role == "user").first().id

        print(user.role)
        
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_all_users_paginated(page=1, per_page=10):
        query = User.query.order_by(User.email)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return pagination.items, pagination.total

    @staticmethod
    def update_user(user_id, update_data):
        user = User.query.get(user_id)
        if not user:
            return None

        if 'email' in update_data:
            # Verifica se la nuova email è già in uso
            existing = User.query.filter(
                User.email == update_data['email'],
                User.id != user_id
            ).first()
            if existing:
                raise ValueError("Email already in use")
            user.email = update_data['email']

        if 'password' in update_data:
            user.password = update_data['password']

        if 'image' in update_data:
            user.image = update_data['image']

        if 'name' in update_data:
            user.name = update_data['name']

        db.session.commit()
        return user

    @staticmethod
    def delete_user(user_id):
        user = User.query.get(user_id)
        if not user:
            return False
        
        user.deleted_at = datetime.now()
            
        db.session.commit()
        return True

    @staticmethod
    def search_users(query):
        return User.query.filter(
            or_(
                User.username.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%')
            )
        ).limit(20).all()