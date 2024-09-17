from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
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
def fetch_all_messages(
    user: str,
    background_tasks: BackgroundTasks,
    first: int = None,
    last: int = None,
    db: Session = Depends(get_db),
):
    background_tasks.add_task(update_fetched_messages, db, user)
    db_messages = crud.fetch_messages(db, recipient=user, first=first, last=last)
    return db_messages


@app.get("/messages/new-messages/{user}", response_model=list[schemas.Message])
def fetch_new_messages(
    user: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    background_tasks.add_task(update_fetched_messages, db, user)
    db_message = crud.fetch_new_messages(db, user)
    return db_message


@app.post("/messages/", response_model=schemas.Message)
def send_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    db_message = crud.post_message(db, message=message)
    return db_message


@app.post("/messages/delete")
def delete_messages(ids: list[int], db: Session = Depends(get_db)):
    num_messages_deleted = crud.delete_messages(db, ids=ids)
    if num_messages_deleted == 0:
        return {"msg": "No messages deleted"}
    return {"Number of msgs deleted": num_messages_deleted}


@app.delete("/messages/{id}", status_code=204)
def delete_message(id: int, db: Session = Depends(get_db)):
    num_messages_deleted = crud.delete_messages(db, ids=[id])
    if num_messages_deleted == 0:
        raise HTTPException(status_code=404, detail="Message not found")
    return
