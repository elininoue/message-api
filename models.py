import datetime
from .database import Base
from sqlalchemy import Boolean, Column, Integer, String, DateTime, func


def current_utc_timestamp():
    return datetime.datetime.now(datetime.timezone.utc)


class Messages(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipient = Column(String)
    sender = Column(String)
    fetched = Column(Boolean, default=False)
    time_sent = Column(
        DateTime, nullable=False, default=current_utc_timestamp
    )  # TODO: Handle time zones
    content = Column(String)
