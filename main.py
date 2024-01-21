from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

import crud
import models
import schemas
from auth import get_user
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)
app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/private/announcements", response_model=schemas.Announcement)
def create_announcement(announcement: schemas.AnnouncementCreate, db: Session = Depends(get_db)):
    return crud.create_announcement(db=db, announcement=announcement)


@app.get("/public/announcements", response_model=list[schemas.AnnouncementList])
def get_announcements(db: Session = Depends(get_db), user: str = Depends(get_user)):
    return crud.get_announcements(db=db, user=user)


@app.post("/public/token", response_model=schemas.NotificationToken)
def create_token(token: schemas.NotificationToken, db: Session = Depends(get_db), user: str = Depends(get_user)):
    return crud.create_token(db=db, token=token.token, user=user)
