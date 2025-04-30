from models.comment import Comment
from database import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from controllers.post import PostService

class CommentService:
    @staticmethod
    def get_all_comment(post_id, include_deleted=False):
        """Ottieni tutti i post (esclusi quelli cancellati)"""
        post = PostService.get_post_by_id(post_id)
        if not post:
            raise Exception("Post not found.")
        
        query = Comment.query.filter(Comment.post_id == post_id)
        if not include_deleted:
            query = query.filter(Comment.deleted_at == None)

        return query.order_by(Comment.created_at.desc()).all()

    @staticmethod
    def get_comment_by_id(post_id, comment_id, include_deleted=False):
        """Ottieni un post specifico per ID"""
        post = PostService.get_post_by_id(post_id)

        if not post: return None

        query = Comment.query.filter(Comment.id == comment_id)
        if not include_deleted:
            query = query.filter(Comment.deleted_at == None)
        
        result = query.first()

        if result is None or post.id != result.post_id:
            return None

        return result

    @staticmethod
    def create_comment(comment_data):
        """Crea un nuovo post"""
        post = PostService.get_post_by_id(comment_data["post_id"])
        if not post:
            raise Exception("Post not found.")
        
        try:
            comment = Comment(**comment_data)

            db.session.add(comment)
            db.session.commit()
            return comment
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

    @staticmethod
    def soft_delete_post(id):
        """Eliminazione logica del post"""
        comment = Comment.query.get(id)
        if not comment or comment.deleted_at is not None:
            return False

        try:
            comment.deleted_at = datetime.now()
            db.session.commit()
            return True
        except SQLAlchemyError:
            db.session.rollback()
            return False
