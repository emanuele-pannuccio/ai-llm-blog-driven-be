from flask import Flask, request, jsonify
from flask_jwt_extended import set_access_cookies, get_jwt, current_user, unset_jwt_cookies
from flask_jwt_extended.exceptions import RevokedTokenError
from flask_cors import CORS
from datetime import datetime, timezone, timedelta


from database import db
from jwt_auth import jwt

from views.user import user_bp
from views.auth import auth_bp
from views.post import post_bp
from views.tag import tag_bp
from views.category import category_bp


# region MODELS

from models.role import Role
from models.post_rel import *
from models.post_status import PostStatus
from models.category import Category
from models.post import Post
from models.tag import Tag
from models.token import Token
from models.user import User

from config import Config

#endregion

import os

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    app.config['SQLALCHEMY_ECHO'] = True

    # Inizializza il database
    CORS(app, supports_credentials=True)

    db.init_app(app)

    jwt.init_app(app)
    
    # Registra i blueprint
    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(tag_bp)
    app.register_blueprint(category_bp)
    
    return app

app = create_app()

@app.teardown_appcontext
def remove_session(exception=None):
    db.session.remove()

@app.get('/')
def healthy():
    return jsonify(ok=True), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crea tutte le tabelle
        
        if not Category.query.first():
            for cat_name, image in {
                "AWS" : "https://assets.intersystems.com/26/bd/6a6aa762425f87ad7d5c2fe65f8c/awslogo-image.jpg", 
                "GCP" : "https://www.sonata-software.com/sites/default/files/banner/image/2022-11/GCP-banner.webp", 
                "Kubernetes" : "https://miro.medium.com/v2/resize:fit:1136/1*SG-XCUpGkO8hT5kgA6FEXg.png", 
                "AI" : "https://png.pngtree.com/thumb_back/fh260/background/20210906/pngtree-ai-artificial-intelligence-starry-sky-portrait-blue-technology-banner-image_804237.jpg" 
            }.items():
                cat = Category(name=cat_name, image=image)
                db.session.add(cat)
                db.session.commit()

        if not Role.query.first():
            for role_name in ["user", "admin"]:
                role = Role(role=role_name)
                db.session.add(role)
                db.session.commit()

        if not PostStatus.query.first():
            for status in ["review", "public"]:
                status_orm = PostStatus(status=status)
                db.session.add(status_orm)
                db.session.commit()

    app.run(host='0.0.0.0', port=Config.PORT, debug=True)