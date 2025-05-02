from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, event
from sqlalchemy.orm import ORMExecuteState, Session, sessionmaker, with_loader_criteria

from models.utils.soft_delete_query import SoftDeleteMixin

from datetime import datetime
from zoneinfo import ZoneInfo

db = SQLAlchemy()


@event.listens_for(db.session, "do_orm_execute")
def _add_filtering_criteria(execute_state):
    from models.post import Post
    
    if (
        execute_state.is_select
        and not execute_state.execution_options.get("include_deleted", False)
    ):
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                SoftDeleteMixin,
                lambda cls: cls.deleted_at == None,
                include_aliases=True
            )
        )

    if (
        execute_state.is_select
        and not execute_state.execution_options.get("include_all", False)
    ):
        now_rome = datetime.now(ZoneInfo("Europe/Rome"))

        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                Post,
                lambda cls: (cls.status.has(status="public")) & (cls.created_at <= now_rome),
                include_aliases=True
            )
        )