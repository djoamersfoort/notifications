from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import models
import schemas
from auth import get_user
from database import engine, get_db

app = FastAPI()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield

@app.post("/private/announcements", response_model=schemas.Announcement)
async def create_announcement(announcement: schemas.AnnouncementCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_announcement(db=db, announcement=announcement)


@app.get("/public/announcements", response_model=list[schemas.AnnouncementList])
async def get_announcements(db: AsyncSession = Depends(get_db), user: str = Depends(get_user)):
    return await crud.get_announcements(db=db, user_id=user)


@app.post("/public/token", response_model=schemas.NotificationToken)
async def create_token(token: schemas.NotificationToken, db: AsyncSession = Depends(get_db), user: str = Depends(get_user)):
    return await crud.create_token(db=db, token=token.token, user_id=user)
