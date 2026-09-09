import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, JSON, Uuid

from database import Base


class Game(Base):
    __tablename__ = "games"

    session_id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ships = Column(JSON, nullable=False)
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(DateTime, nullable=False, default=datetime.now)
