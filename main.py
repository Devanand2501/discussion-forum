from fastapi import FastAPI, HTTPException
from typing import List
import os
from pymongo import MongoClient
from pydantic import BaseModel
from bson import ObjectId
from dotenv import load_dotenv
load_dotenv()

# MongoDB connection
url = os.getenv("ATLAS_URL")
database = os.getenv("DB_NAME")
discussion = os.getenv("DISCUSSION_COLLECTION")
users = os.getenv("USER_COLLECTION")
client = MongoClient(url)
db = client[database]
discussion_collection = db[discussion]
users_collection = db[users]
# print("url-->",url)
# print("database-->",database)
# print("disucssion collection-->",disucssion)
# print("user collection-->",users)

# User model
class User(BaseModel):
    name: str
    mobile: str
    email: str

# User class
class UserClass:
    def __init__(self, name: str, mobile: str, email: str, id: str = None):
        self.id = id
        self.name = name
        self.mobile = mobile
        self.email = email

    def to_dict(self):
        return {
            "name": self.name,
            "mobile": self.mobile,
            "email": self.email
        }


# FastAPI instance
app = FastAPI()

# Create User
@app.post("/create_user/")
async def create_user(user: User):
    if users_collection.find_one({"mobile": user.mobile}) or users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Mobile number or email already exists")
    user_obj = UserClass(**user.model_dump())
    inserted_user = users_collection.insert_one(user_obj.to_dict())
    return {"message": "User created successfully", "user_id": str(inserted_user.inserted_id)}

# Read Users
@app.get("/all_users/")
async def read_users():
    users = list(users_collection.find())
    formatted_users = []
    for user in users:
        user["_id"] = str(user["_id"])
        formatted_users.append(user)
    return formatted_users

# Search User by name
@app.get("/search_users/")
async def search_user(name: str):
    users = list(users_collection.find({"name": {"$regex": name, "$options": "i"}}))
    formatted_users = []
    for user in users:
        user["_id"] = str(user["_id"])
        formatted_users.append(user)
    return formatted_users

# Update User
@app.put("/update_user/{user_id}")
async def update_user(user_id: str, user: User):
    updated_user = users_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$set": user.model_dump()})
    if updated_user.modified_count == 1:
        return {"message": "User updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

# Delete User
@app.delete("/delete_user/{user_id}")
async def delete_user(user_id: str):
    deleted_user = users_collection.delete_one({"_id": ObjectId(user_id)})
    if deleted_user.deleted_count == 1:
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")
