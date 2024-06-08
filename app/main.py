from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bson import ObjectId
from .crud import retrieve_users, add_user, retrieve_user, delete_user as delete_user_crud, update_user as update_user_crud
from typing import List
from .models import User


app = FastAPI()

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    age: int
    photo_directory: str
    face_encoding: str

@app.post("/users/", response_model=UserCreate)
async def create_user(user: UserCreate):
    user_dict = user.dict()
    result = await add_user(user)
    if result:
        return result
    raise HTTPException(status_code=400, detail="User not created")

@app.get("/users/", response_model=List[UserCreate])
async def get_users():
    users = await retrieve_users()
    return users

@app.get("/users/{id}", response_model=UserCreate)
async def get_user(id: str):
    user = await retrieve_user(id)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

@app.put("/users/{id}", response_model=User)
async def update_user(id: str, user: UserCreate):
    updated_user = await update_user_crud(id, user)
    if updated_user:
        return updated_user
    raise HTTPException(status_code=404, detail="User not found")

@app.delete("/users/{id}")
async def delete_user(id: str):
    user = await delete_user_crud(id)  # Corregir esta línea
    if user:
        return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")
