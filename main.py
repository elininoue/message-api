from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

MAXIMUM_REQUEST_LIMIT = 500
DEFAULT_NUM_MSGS = 100

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


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


# Method for retrieving new messages and all messages within a specified range.
@app.get("/v1/messages/{user}", response_model=list[schemas.Message])
def fetch_all_messages(
    user: str,
    background_tasks: BackgroundTasks,
    offset: int = 0,
    limit: int = DEFAULT_NUM_MSGS,
    new_only: bool = False,
    db: Session = Depends(get_db),
):

    # Return error response if offset is invalid
    if offset < 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid offset. Offset needs to be a positive integer.",
        )

    # Return error response if client requests too many messages at once.
    # A precaution to avoid sending responses with a lot of data, putting a high load on the server.
    if limit > MAXIMUM_REQUEST_LIMIT:
        raise HTTPException(
            status_code=400,
            detail=f"Too many messages requested. The maximum limit is {MAXIMUM_REQUEST_LIMIT}.",
        )

    # Update the messages to reflect that they have been fetched.
    # Updated AFTER sending response so client can see what has been fetched previously.
    background_tasks.add_task(update_fetched_messages, db, user)
    db_messages = crud.fetch_messages(
        db, recipient=user, first=offset, last=limit, new_only=not (new_only)
    )
    return db_messages


# Method for sending messages
@app.post("/v1/messages/", response_model=schemas.Message)
def send_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    db_message = crud.post_message(db, message=message)
    return db_message


# Method for deleting multiple messages. Multiple messages are deleted using a post request
# instead of delete, since some clients don't support a request body for delete requests.
@app.post("/v1/messages/delete")
def delete_messages(ids: list[int], db: Session = Depends(get_db)):
    num_messages_deleted = crud.delete_messages(db, ids=ids)
    if num_messages_deleted == 0:
        raise HTTPException(status_code=404, detail="Messages not found")
    return {"total": num_messages_deleted}


# Method for deleting a single message.
@app.delete("/v1/messages/{id}", status_code=204)
def delete_message(id: int, db: Session = Depends(get_db)):
    num_messages_deleted = crud.delete_messages(db, ids=[id])
    if num_messages_deleted == 0:
        raise HTTPException(status_code=404, detail="Message not found")
    return
