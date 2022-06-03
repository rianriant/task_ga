from typing import Union
from datetime import datetime
from pydantic import BaseModel


class FileRecord(BaseModel):
    code: int
    filename: str
    registration_datetime: Union[str, None] = None

    class Config:
        orm_mode = True
