import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
import schemas


async def get_user(db: AsyncSession, user: str) -> models.User:
    results = await db.execute(
        select(models.User)
        .where(models.User.id == user)
        .options(selectinload(models.User.announcements))
    )
    db_user = results.scalar_one_or_none()
    if db_user is None:
        db_user = models.User(id=user)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

    return db_user


async def create_announcement(db: AsyncSession, announcement: schemas.AnnouncementCreate) -> models.Announcement:
    print(f"Sending notification {announcement.title} to {len(announcement.recipients)} users")
    recipients = []
    tokens = []
    for recipient in announcement.recipients:
        user = await get_user(db, recipient)
        recipients.append(user)
        for token in user.tokens:
            tokens.append(token.token)

    print(f"Found {len(recipients)} registered users and {len(tokens)} relevant tokens")
    db_announcement = models.Announcement(title=announcement.title, description=announcement.description,
                                          content=announcement.content, recipients=recipients)
    db.add(db_announcement)
    await db.commit()
    await db.refresh(db_announcement)

    http = httpx.AsyncClient(timeout=10)
    for token in tokens:
        result = await http.post("https://exp.host/--/api/v2/push/send", json={
            "to": token,
            "title": announcement.title,
            "body": announcement.description
        })
        if result.is_error:
            print(f"Oeps, er ging iets mis {result.content}")

    return db_announcement


async def get_announcements(db: AsyncSession, user: str) -> list[models.Announcement]:
    user = await get_user(db, user)
    return user.announcements


async def create_token(db: AsyncSession, user: str, token: str) -> models.NotificationToken:
    user = await get_user(db, user)
    results = await db.execute(
        select(models.NotificationToken).where(models.NotificationToken.token == token)
    )
    db_token: models.NotificationToken | None = results.scalar_one_or_none()
    if db_token is not None:
        db_token.user = user
        await db.commit()
        return db_token

    db_token = models.NotificationToken(user=user, token=token)
    db.add(db_token)
    await db.commit()
    await db.refresh(db_token)
    return db_token
