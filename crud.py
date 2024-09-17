from sqlalchemy.orm import Session

from . import models, schemas


def fetch_messages(
    db: Session,
    recipient: str,
    fetch_old: bool,
    first: int,
    last: int,
):
    return (
        db.query(models.Messages)
        .filter(
            models.Messages.recipient == recipient, models.Messages.fetched == fetch_old
        )
        .order_by(models.Messages.time_sent.desc())[first:last]
    )


def delete_messages(db: Session, ids: list[int]):
    deleted = (
        db.query(models.Messages)
        .filter(models.Messages.id.in_(ids))
        .delete(synchronize_session=False)
    )
    db.commit()
    return deleted


def post_message(db: Session, message: schemas.MessageCreate):
    db_message = models.Messages(
        content=message.content, recipient=message.recipient, sender=message.sender
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
