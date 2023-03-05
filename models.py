import uuid
from database import Base
from sqlalchemy import TIMESTAMP, Column, String, Integer, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID


class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    first_name = Column(String,  nullable=False)
    last_name = Column(String,  nullable=False)
    username = Column(String,  unique=True, nullable=False)
    password = Column(String, nullable=False)

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key = True, autoincrement = True)
    title = Column(String,  nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id))
