from fastapi import BackgroundTasks, Depends, FastAPI
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def update_fetched_messages(db: Session, recipient: str):
    db.query(models.Messages).filter(models.Messages.recipient == recipient).update(
        {"fetched": True}
    )
    db.commit()


@app.get("/messages/{user}", response_model=list[schemas.Message])
def fetch_messages(
    user: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    background_tasks.add_task(update_fetched_messages, db, user)
    db_messages = crud.fetch_messages(db, recipient=user)
    return db_messages


@app.post("/messages/", response_model=schemas.Message)
def send_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    db_message = crud.post_message(db, message=message)
    return db_message
