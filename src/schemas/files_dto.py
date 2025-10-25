from io import IOBase
from pydantic import BaseModel
from typing import Optional


class FileDTO(BaseModel):
    filename: str
    content_type: Optional[str] = None
    file: IOBase

    class Config:
        arbitrary_types_allowed = True
