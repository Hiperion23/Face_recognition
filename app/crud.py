from .database import user_collection
from .models import User
from .schemas import UserCreate
from bson import ObjectId
import os
from pathlib import Path
import shutil

def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "age": user["age"],
        "photo_directory": user["photo_directory"],
        "face_encoding": user["face_encoding"]
    }

async def retrieve_users():
    users = []
    for user in user_collection.find():
        users.append(user_helper(user))
    return users

async def add_user(user_data: UserCreate):
    user_dict = user_data.dict()
    user = user_collection.insert_one(user_dict)
    new_user = user_collection.find_one({"_id": user.inserted_id})
    user_id = str(new_user["_id"])
    photo_directory = f"face_recognition/known_faces/user_{user_id}"
    Path(photo_directory).mkdir(parents=True, exist_ok=True)
    user_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"photo_directory": photo_directory}})
    return user_helper(new_user)

async def retrieve_user(id: str):
    user = user_collection.find_one({"_id": ObjectId(id)})
    if user:
        return user_helper(user)

async def update_user(id: str, data: UserCreate):
    user = user_collection.find_one({"_id": ObjectId(id)})
    if user:
        updated_user = user_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": data.dict()}
        )
        if updated_user.modified_count:
            new_user = user_collection.find_one({"_id": ObjectId(id)})
            return user_helper(new_user)
    return False

async def delete_user(id: str):
    user = user_collection.find_one({"_id": ObjectId(id)})
    if user:
        user_collection.delete_one({"_id": ObjectId(id)})
        user_directory = Path(user["photo_directory"])
        if user_directory.exists():
            shutil.rmtree(user_directory)
        return True
    return False
