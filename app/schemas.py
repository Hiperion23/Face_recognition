from pydantic import BaseModel
from typing import List

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    age: int
    photo_directory: str
    face_encoding: List[float]

class User(BaseModel):
    id: str
    first_name: str
    last_name: str
    age: int
    photo_directory: str
    face_encoding: List[float]

    class Config:
        orm_mode = True
