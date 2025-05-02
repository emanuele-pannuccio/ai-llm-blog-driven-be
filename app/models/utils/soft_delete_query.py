from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import Column, Boolean, DateTime
from sqlalchemy.orm import declarative_mixin

@declarative_mixin
class SoftDeleteMixin:
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    def soft_delete(self):
        self.deleted_at = datetime.now(ZoneInfo("Europe/Rome"))
