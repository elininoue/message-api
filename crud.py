from sqlalchemy.orm import Session
import copy

from . import models, schemas


def fetch_new_messages(db: Session, recipient: str):
    return db.query(models.Messages).filter(
        models.Messages.recipient == recipient, models.Messages.fetched == False
    )


# TODO: Add range specifiers and order results based on time
def fetch_messages(db: Session, recipient: str):
    messages = db.query(models.Messages).filter(models.Messages.recipient == recipient).all()
    return messages


def delete_message(db: Session, id: int):
    # TODO
    pass


def delete_messages(db: Session, ids: list[int]):
    # TODO
    pass


def post_message(db: Session, message: schemas.MessageCreate):
    db_message = models.Messages(
        content=message.content, recipient=message.recipient, sender=message.sender
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
