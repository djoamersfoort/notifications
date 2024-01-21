from datetime import datetime

from pydantic import BaseModel


class Announcement(BaseModel):
    title: str
    description: str
    content: str


class AnnouncementCreate(Announcement):
    recipients: list[str]


class AnnouncementList(Announcement):
    date: datetime


class NotificationToken(BaseModel):
    token: str
