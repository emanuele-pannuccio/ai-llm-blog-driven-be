from models.tag import Tag
from models.post import Post

from database import db
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

class TagService:
    @staticmethod
    def get_all_tags(sort_by=None, sort_order=None):
        query = db.session.query(Tag).join(Tag.posts).filter(Post.created_at != None)
        
        if sort_by == "posts":
            query = query.group_by(Tag.id)
            sort_by = db.func.count(Tag.id)

        if sort_order == 'asc':
            query = query.order_by(sort_by.desc())
        elif sort_order == "desc":
            query = query.order_by(sort_by.asc())


        return query.all()

    @staticmethod
    def get_tag_by_id(tag_id: int):
        tag = Tag.query.get(tag_id)
        if not tag:
            raise NoResultFound(f"Tag with id {tag_id} not found")
        return tag

    @staticmethod
    def create_tag(tag_data: dict):
        tag_ = Tag.query.filter(Tag.tag == tag_data["tag"]).one_or_none()

        if tag_ is not None: return tag_

        new_tag = Tag(**tag_data)
        db.session.add(new_tag)
        db.session.commit()
        return new_tag

    @staticmethod
    def update_tag(tag_id: int, update_data: dict):
        tag = TagService.get_tag_by_id(tag_id)
        for key, value in update_data.items():
            setattr(tag, key, value)
        db.session.commit()
        db.session.refresh(tag)
        return tag

    @staticmethod
    def delete_tag(tag_id: int):
        tag = TagService.get_tag_by_id(tag_id)
        db.session.delete(tag)
        db.session.commit()
        return {"message": f"Tag with id {tag_id} deleted"}