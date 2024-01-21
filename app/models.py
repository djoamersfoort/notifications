from uuid import uuid4

from sqlalchemy import Column, String, Uuid, ForeignKey, DateTime
from sqlalchemy import Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base

association_table = Table(
    'announcements_associations', Base.metadata,
    Column('users', String, ForeignKey('users.id')),
    Column('announcements', Uuid, ForeignKey('announcements.id'))
)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    announcements = relationship("Announcement", secondary=association_table, back_populates="recipients")
    tokens = relationship("NotificationToken", back_populates="user")


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Uuid, primary_key=True, index=True, default=uuid4)
    date = Column(DateTime(timezone=True), server_default=func.now())
    title = Column(String)
    description = Column(String)
    content = Column(String)
    recipients = relationship("User", secondary=association_table, back_populates="announcements")


class NotificationToken(Base):
    __tablename__ = "notification_tokens"

    id = Column(Uuid, primary_key=True, index=True, default=uuid4)
    user_id = Column(String, ForeignKey("users.id"))
    user = relationship("User", back_populates="tokens")
    token = Column(String)
