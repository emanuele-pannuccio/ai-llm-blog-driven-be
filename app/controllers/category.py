from database import db
from math import ceil

from datetime import datetime

from models.category import Category
from models.post import Post

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import SQLAlchemyError

class CategoryService:
    @staticmethod
    def delete_category(cat_id):
        """Eliminazione logica del post"""
        cat = Category.query.get(cat_id)
        if not cat:
            raise Exception("Categoria non trovata.")
        
        if cat and len(cat.posts) > 0:
            for post in cat.posts:
                post.status_id = 1
                post.category_id = None
                # Essendo che li vado ad eliminare, la categoria, va scelta una categoria di rimpiazzo nel caso in cui non venga indicata
        
        try:
            db.session.delete(cat)
            db.session.commit()
            return True
        except SQLAlchemyError:
            db.session.rollback()
            return False


    @staticmethod
    def create_category(name):
        if not name:
            raise ValueError("Missing category name.")

        existing_category = Category.query.filter_by(name=name).first()
        if existing_category:
            raise ValueError("Category already exists.")

        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        return category

    @staticmethod
    def get_category(category_id):
        category = Category.query.get(category_id)
        if not category:
            raise NoResultFound("Category not found")
        return category

    @staticmethod
    def get_category_by_name(name):
        category = Category.query.filter(Category.name == name).one_or_none()
        if not category:
            raise NoResultFound("Category not found")
        return category
    
    @staticmethod
    def list_categories(**kwargs):
        name_filter = kwargs.get("name")
        page = kwargs.get('page', 1)
        per_page = kwargs.get('per_page', 10)
        admin = kwargs.get('admin', 10)

        query = db.session.query(Category)

        if admin:
            query = query.execution_options(include_all=True)
            
        if name_filter:
            query = query.filter(Category.name.ilike(f"%{name_filter}%"))

        
        total_count = query.count()
        total_pages = ceil(total_count / per_page) if per_page else 1
        
        if page is not None and page > total_pages:
            return [], 0, 1, 0
        
        if page is not None and per_page is not None:
            query = query.offset((page - 1) * per_page).limit(per_page)
        else:
            total_pages = 1

        return query.all(), total_pages, page, total_count