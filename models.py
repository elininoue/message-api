import datetime
from .database import Base
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func


class Messages(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipient = Column(String)
    sender = Column(String)
    fetched = Column(Boolean, default=False)
    time_sent = Column(
        DateTime, default=datetime.datetime.now()
    )  # TODO: Handle time zones
    content = Column(String)
