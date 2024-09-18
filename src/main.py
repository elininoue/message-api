from typing import Annotated
from fastapi import BackgroundTasks, Body, Depends, FastAPI, HTTPException
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
    start_at: int = 0,
    stop_at: int = None,
    new_only: bool = False,
    db: Session = Depends(get_db),
):

    # If no stop index is provided, fetch a default number of messages
    if stop_at == None:
        stop_at = start_at + DEFAULT_NUM_MSGS

    # Return error response if start index is invalid
    if start_at < 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid index. Start index needs to be a positive integer.",
        )

    # Return error response if stop index is invalid
    if stop_at < 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid index. Stop index needs to be a positive integer.",
        )

    # Return error response if client requests too many messages at once.
    # A precaution to avoid sending responses with a lot of data, putting a high load on the server.
    if stop_at - start_at > MAXIMUM_REQUEST_LIMIT:
        raise HTTPException(
            status_code=400,
            detail=f"Too many messages requested. The maximum limit is {MAXIMUM_REQUEST_LIMIT}.",
        )

    # Update the messages to reflect that they have been fetched.
    # Updated AFTER sending response so client can see what has been fetched previously.
    background_tasks.add_task(update_fetched_messages, db, user)
    db_messages = crud.fetch_messages(
        db, recipient=user, first=start_at, last=stop_at, fetch_old=not (new_only)
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
def delete_messages(
    ids: Annotated[list[int], Body(embed=True)], db: Session = Depends(get_db)
):
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
