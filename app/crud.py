import requests
from sqlalchemy.orm import Session

import models
import schemas


def get_user(db: Session, user: str):
    db_user = db.query(models.User).filter(models.User.id == user).first()
    if db_user is None:
        db_user = models.User(id=user)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    return db_user


def create_announcement(db: Session, announcement: schemas.AnnouncementCreate):
    recipients = []
    tokens = []
    for recipient in announcement.recipients:
        user = get_user(db, recipient)
        recipients.append(user)
        for token in user.tokens:
            tokens.append(token.token)

    db_announcement = models.Announcement(title=announcement.title, description=announcement.description,
                                          content=announcement.content, recipients=recipients)
    db.add(db_announcement)
    db.commit()
    db.refresh(db_announcement)

    requests.post("https://api.expo.dev/v2/push/send", json={
        "to": tokens,
        "title": announcement.title,
        "body": announcement.description
    }, timeout=10)
    return db_announcement


def get_announcements(db: Session, user: str):
    return get_user(db, user).announcements


def create_token(db: Session, user: str, token: str):
    user = get_user(db, user)
    db_token = db.query(models.NotificationToken).filter(models.NotificationToken.token == token).first()
    if db_token is not None:
        db_token.user = user
        db.commit()
        return db_token

    db_token = models.NotificationToken(user=user, token=token)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token
