from typing import Sequence

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
    # Fetch all users and their tokens
    result = await db.execute(
        select(models.User)
        .where(models.User.id.in_(announcement.recipients))
        .options(selectinload(models.User.tokens))
    )
    users = result.scalars().all()

    # Collect tokens for the push service
    tokens = []
    for user in users:
        for token in user.tokens:
            tokens.append(token.token)

    print(f"Found {len(users)} registered users and {len(tokens)} relevant tokens")

    # Create the announcement
    db_announcement = models.Announcement(
        title=announcement.title,
        description=announcement.description,
        content=announcement.content,
        recipients=users
    )

    db.add(db_announcement)
    await db.commit()
    await db.refresh(db_announcement)

    # Send notifications
    async with httpx.AsyncClient(timeout=10) as http:
        for token in tokens:
            result = await http.post("https://exp.host/--/api/v2/push/send", json={
                "to": token,
                "title": announcement.title,
                "body": announcement.description
            })
            if result.is_error:
                print(f"Oeps, er ging iets mis: {result.text}")

    return db_announcement

async def get_announcements(db: AsyncSession, user_id: str) -> Sequence[models.Announcement]:
    result = await db.execute(
        select(models.Announcement)
        .join(models.Announcement.recipients)
        .where(models.User.id == user_id)
    )
    return result.scalars().all()

async def create_token(db: AsyncSession, user: str, token: str) -> models.NotificationToken:
    user = await get_user(db, user)
    results = await db.execute(
        select(models.NotificationToken).where(models.NotificationToken.token == token)
    )
    db_token: models.NotificationToken | None = results.scalar_one_or_none()
    if db_token is None:
        # Create a new token
        db_token = models.NotificationToken(user=user, token=token)
        db.add(db_token)

    # Update the token with the user
    db_token.user = user
    await db.commit()
    await db.refresh(db_token)
    return db_token
