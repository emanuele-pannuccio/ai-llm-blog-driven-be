
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.orm import ORMExecuteState
from sqlalchemy import event
from datetime import datetime

from flask_jwt_extended import current_user, verify_jwt_in_request
from flask import g

from database import db

from models.tag import Tag
from models.post_rel import *

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text)
    image = db.Column(db.String(255))
    publisher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('post_status.id'))
    created_at = db.Column(db.TIMESTAMP, default=datetime.now())
    deleted_at = db.Column(db.TIMESTAMP, default=None)
    
    # Relazioni
    user = db.relationship("User", back_populates="posts")
    tags = db.relationship("Tag", secondary=post_tags, back_populates="posts")
    category = db.relationship("Category", back_populates="posts")
    comments = db.relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    status = db.relationship("PostStatus", back_populates="posts")


# @event.listens_for(db.session.__class__, "do_orm_execute")
# def _add_filtering_criteria(execute_state: ORMExecuteState):
#     try:
#         is_admin = current_user != None and current_user.role.role == "admin" and g.get("bypass_filter")
#     except:
#         is_admin = False
    
#     if execute_state.is_select and not is_admin:
#         now = datetime.now()
#         execute_state.statement = execute_state.statement.options(
#             with_loader_criteria(
#                 Post,
#                 lambda cls: (
#                     (cls.deleted_at == None) &
#                     (cls.created_at != None) &
#                     (cls.status_id == 2) &
#                     (cls.publisher_id != None) &
#                     (cls.created_at <= now)
#                 )
#             )
#         )
