from fastapi import FastAPI, HTTPException,Query
from typing import List,Optional
from datetime import datetime
import os
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId
from dotenv import load_dotenv
load_dotenv()

# MongoDB connection
url = os.getenv("ATLAS_URL")
database = os.getenv("DB_NAME")
discussions = os.getenv("DISCUSSION_COLLECTION")
users = os.getenv("USER_COLLECTION")
client = MongoClient(url)
db = client[database]
discussion_collection = db[discussions]
user_collection = db[users]
# print("url-->",url)
# print("database-->",database)
# print("disucssion collection-->",disucssion)
# print("user collection-->",users)

# User model
class User(BaseModel):
    name: str
    mobile: str
    email: str

# Discussion Model
class Discussion(BaseModel):
    text: str
    image: Optional[str] = None 
    hashtags: List[str]
    created_on: datetime = datetime.now()

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

# Discussion class
class DiscussionClass:
    def __init__(self, text: str, image: Optional[str], hashtags: List[str], created_on: datetime = datetime.now(), id: str = None):
        self.id = id
        self.text = text
        self.image = image
        self.hashtags = hashtags
        self.created_on = created_on

    def to_dict(self):
        return {
            "text": self.text,
            "image": self.image,
            "hashtags": self.hashtags,
            "created_on": self.created_on
        }

# FastAPI instance
app = FastAPI()

# Create User
@app.post("/create_user/")
async def create_user(user: User):
    if user_collection.find_one({"mobile": user.mobile}) or user_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Mobile number or email already exists")
    user_obj = UserClass(**user.model_dump())
    inserted_user = user_collection.insert_one(user_obj.to_dict())
    return {"message": "User created successfully", "user_id": str(inserted_user.inserted_id)}

# Read Users
@app.get("/all_users/")
async def read_users():
    users = list(user_collection.find())
    formatted_users = []
    for user in users:
        user["_id"] = str(user["_id"])
        formatted_users.append(user)
    return formatted_users

# Search User by name
@app.get("/search_users/")
async def search_user(name: str):
    users = list(user_collection.find({"name": {"$regex": name, "$options": "i"}}))
    formatted_users = []
    for user in users:
        user["_id"] = str(user["_id"])
        formatted_users.append(user)
    return formatted_users

# Update User
@app.put("/update_user/{user_id}")
async def update_user(user_id: str, user: User):
    updated_user = user_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$set": user.model_dump()})
    if updated_user.modified_count == 1:
        return {"message": "User updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

# Delete User
@app.delete("/delete_user/{user_id}")
async def delete_user(user_id: str):
    deleted_user = user_collection.delete_one({"_id": ObjectId(user_id)})
    if deleted_user.deleted_count == 1:
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

# Create Discussion
@app.post("/create_discussion/")
async def create_discussion(discussion: Discussion):
    discussion_obj = DiscussionClass(**discussion.dict())
    inserted_discussion = discussion_collection.insert_one(discussion_obj.to_dict())
    return {"message": "Discussion created successfully", "discussion_id": str(inserted_discussion.inserted_id)}

# Update Discussion
@app.put("/update_discussion/{discussion_id}")
async def update_discussion(discussion_id: str, discussion: Discussion):
    updated_discussion = discussion_collection.update_one(
        {"_id": ObjectId(discussion_id)}, {"$set": discussion.dict()})
    if updated_discussion.modified_count == 1:
        return {"message": "Discussion updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Discussion not found")

# Delete Discussion
@app.delete("/delete_discussion/{discussion_id}")
async def delete_discussion(discussion_id: str):
    deleted_discussion = discussion_collection.delete_one({"_id": ObjectId(discussion_id)})
    if deleted_discussion.deleted_count == 1:
        return {"message": "Discussion deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Discussion not found")

# Get list of discussions based on tags
@app.get("/discussions/tags/")
async def get_discussions_by_tags(tags: str = Query(...)):
    tag_list = tags.split(",")
    print(tags)
    # documents = discussion_collection.find({
    #     "hashtags": {"$regex": f"#{tags}", "$options": "i"} 
    # })
    documents = discussion_collection.find({
        "hashtags": {"$in": [f"#{tag}" for tag in tag_list]} 
    })
    # for doc in documents:
    #     print(doc)
    formatted_discussions = []
    for discussion in documents:
        discussion["_id"] = str(discussion["_id"])
        formatted_discussions.append(discussion)
    return formatted_discussions

@app.get("/discussions/text/")
async def get_discussions_by_text(text: str ):
    discussions = list(discussion_collection.find({"text": {"$regex": text, "$options": "i"}}))
    formatted_discussions = []
    for discussion in discussions:
        discussion["_id"] = str(discussion["_id"])
        formatted_discussions.append(discussion)
    return formatted_discussions
