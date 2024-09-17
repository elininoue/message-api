import datetime
from pydantic import BaseModel


class MessageBase(BaseModel):
    content: str
    sender: str
    recipient: str


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    id: int
    fetched: bool
    time_sent: datetime.datetime

    class Config:
        orm_mode = True
