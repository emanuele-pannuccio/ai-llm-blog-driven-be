from datetime import datetime
import math
from flask import g
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from database import db

from controllers.tag import TagService
from controllers.category import CategoryService

from models.post import Post
from models.comment import Comment
from models.tag import Tag
from models.user import User
from models.post_status import PostStatus
from models.category import Category

class PostService:
    @staticmethod
    def get_all_posts(**kwargs):
        """
        Ottieni tutti i post con filtri dinamici.
        Argomenti supportati in kwargs:
            - include_deleted (bool)
            - sort_by (str)
            - sort_order ('asc'|'desc')
            - page (int)
            - per_page (int)
            - tags (list)
            - text (str)
            - category (str)
            - author (int)
            - show_all (bool)
        """
        include_deleted = kwargs.get('include_deleted', False)
        sort_by = kwargs.get('sort_by', 'created_at')
        sort_order = kwargs.get('sort_order', 'desc')
        page = kwargs.get('page', 1)
        per_page = kwargs.get('per_page', 10)
        tags = kwargs.get('tags', [])
        text = kwargs.get('text')
        category = kwargs.get('category')
        author = kwargs.get('author')
        status = kwargs.get('status', None)
        show_all = kwargs.get('show_all', False)

        query = db.session.query(Post)

        if not include_deleted and not show_all:
            now = datetime.now()
            query = query.filter(
                (Post.deleted_at == None) &
                (Post.created_at != None) &
                (Post.status_id == 2) &
                (Post.publisher_id != None) &
                (Post.created_at <= now)
            )

        if text:
            query = query.filter(or_(
                Post.body.contains(text),
                Post.title.contains(text)
            ))

        if category:
            query = query.join(Post.category).filter(Category.name == category)

        if tags:
            query = query.join(Post.tags).filter(Tag.tag.in_(tags)) \
                        .group_by(Post.id) \
                        .having(db.func.count(Tag.id) == len(tags))

        if author:
            query = query.join(Post.user).filter(User.id == author)

        if status:
            query = query.join(Post.status).filter(PostStatus.status == status)
        elif not include_deleted:
            query = query.join(Post.status).filter(PostStatus.status == "public")

        total_count = query.count()
        total_pages = math.ceil(total_count / per_page) if per_page else 1

        if page is not None and page > total_pages:
            return [], 0, 1, 0

        if sort_by == 'comments':
            query = query.outerjoin(Post.comments).group_by(Post.id)
            sort_by = db.func.count(Comment.id)
        else:
            sort_by = getattr(Post, sort_by, Post.created_at)

        if sort_order == 'asc':
            query = query.order_by(sort_by.asc())
        else:
            query = query.order_by(sort_by.desc())

        if page is not None and per_page is not None:
            query = query.offset((page - 1) * per_page).limit(per_page)
        else:
            total_pages = 1

        return query.all(), total_pages, page, total_count


    @staticmethod
    def get_post_by_id(post_id, include_deleted=False, admin=False):
        """Ottieni un post specifico per ID"""
        if admin:
           g.bypass_filter=True
           
        return Post.query.filter(Post.id == post_id).one_or_none()

    @staticmethod
    def create_post(post_data):
        """Crea un nuovo post"""
        try:
            post = Post(
                title=post_data['title'],
                body=post_data.get('body'),
                image=post_data.get('image'),
                publisher_id=post_data['publisher_id'],
                category=CategoryService.get_category_by_name(post_data["category"]),
                status=PostStatus.query.filter(PostStatus.status == post_data["status"]).one_or_none()
            )

            # Gestione tags e categories
            if 'tags' in post_data:
                print(post_data)
                tags_ = []
                for tag in post_data["tags"]:
                    tag_ = TagService.create_tag({"tag":tag})
                    tags_.append(tag_)

                post.tags = tags_
            
            db.session.add(post)
            db.session.commit()
            return post
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

    @staticmethod
    def update_post(post_id, update_data):
        """Aggiorna un post esistente"""
        post = Post.query.get(post_id)
        if not post or post.deleted_at:
            return None

        try:
            if 'title' in update_data:
                post.title = update_data['title']
            if 'body' in update_data:
                post.body = update_data['body']
            if 'image' in update_data:
                post.image = update_data['image']
            
            if 'created_at' in update_data:
                post.created_at = update_data["created_at"]

            post.publisher_id = update_data['user']
            
            # Aggiornamento relazioni
            if 'tags' in update_data:
                tags_ = []
                for tag in update_data["tags"]:
                    tag_ = TagService.create_tag({"tag":tag})
                    tags_.append(tag_)
                post.tags = tags_
                
            if 'category' in update_data:
                category = Category.query.filter(Category.name == update_data["category"]).one_or_none()
                post.category = category

            if 'status' in update_data:
                status = PostStatus.query.filter(PostStatus.status == update_data['status']).one_or_none()
                post.status = status
            
            db.session.commit()
            return post
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

    @staticmethod
    def soft_delete_post(post_id):
        """Eliminazione logica del post"""
        post = Post.query.get(post_id)
        if not post or post.deleted_at is not None:
            return False

        try:
            post.deleted_at = datetime.now()
            post.status = PostStatus.query.filter(PostStatus.status == "archived").one_or_none()
            post.deleted_at = datetime.now()
            db.session.commit()
            return True
        except SQLAlchemyError:
            db.session.rollback()
            return False

    @staticmethod
    def restore_post(post_id):
        """Ripristina un post cancellato logicamente"""
        post = Post.query.get(post_id)
        if not post or post.deleted_at is None:
            return False

        try:
            post.deleted_at = None
            post.created_at = datetime.now()
            post.status = PostStatus.query.filter(PostStatus.status == "review").one_or_none()
            db.session.commit()
            return True
        except SQLAlchemyError:
            db.session.rollback()
            return False