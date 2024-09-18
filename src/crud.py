from sqlalchemy.orm import Session

from . import models, schemas


def fetch_messages(
    db: Session,
    recipient: str,
    fetch_old: bool,
    first: int,
    last: int,
):
    """
    Returns messages within the specified range from the specified database.
    The messages are ordered based on the time they were sent, with most recent messages first.

    :param db: the database session to retrieve messages from
    :param recipient: the user who's messages should be retrieved
    :param first: the start index (inclusive)
    :param last: the stop index (exclusive)
    :param fetch_old: true if messages that have already been fetched should be included, false otherwise
    """

    messages = db.query(models.Messages).filter(models.Messages.recipient == recipient)

    if not (fetch_old):
        messages = messages.filter(models.Messages.fetched == False)

    messages = messages.order_by(models.Messages.time_sent.desc())[first:last]

    return messages


def delete_messages(db: Session, ids: list[int]):
    """
    Removes the specified messages from the database.

    :param db: the database session to remove messages from
    :param ids: a list of ids of the messages to delete
    :return: the number of successfully deleted messages
    """

    deleted = (
        db.query(models.Messages)
        .filter(models.Messages.id.in_(ids))
        .delete(synchronize_session=False)
    )
    db.commit()
    return deleted


def post_message(db: Session, message: schemas.MessageCreate):
    """
    Adds the specified message to the database.

    :param db: the database session to insert message into
    :param message: the message to add
    :return: the message as it appears in the database
    """

    db_message = models.Messages(
        content=message.content, recipient=message.recipient, sender=message.sender
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
