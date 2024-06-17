from fastapi import FastAPI, HTTPException,Query
from typing import List,Optional
from datetime import datetime
import os
from pymongo import MongoClient
from pydantic import BaseModel,Field
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
    followed_users: List[str] = Field(default_factory=list)
    followers: List[str] = Field(default_factory=list)

# Discussion Model
class Discussion(BaseModel):
    text: str
    image: Optional[str] = None 
    hashtags: List[str]
    views: int = 0
    likes: int = 0
    comments: List['Comment'] = []
    created_on: datetime = datetime.now()

# Comment model
class Comment(BaseModel):
    text: str
    author: str
    likes: int = 0
    replies: List['Comment'] = []
    created_on: datetime = datetime.now()

# User class
class UserClass:
    def __init__(self, name: str, mobile: str, email: str, followed_users: List[str] = None, followers: List[str] = None, id: str = None):
        self.id = id
        self.name = name
        self.mobile = mobile
        self.email = email
        self.followed_users = followed_users or []
        self.followers = followers or []

    def to_dict(self):
        return {
            "name": self.name,
            "mobile": self.mobile,
            "email": self.email,
            "followed_users": self.followed_users,
            "followers": self.followers
        }

# Discussion class
class DiscussionClass:
    def __init__(self, text: str, image: Optional[str], hashtags: List[str], created_on: datetime = datetime.now(), views: int = 0, likes: int = 0, comments: List[Comment] = None, id: str = None):
        self.id = id
        self.text = text
        self.image = image
        self.hashtags = hashtags
        self.created_on = created_on
        self.views = views
        self.likes = likes
        self.comments = comments or []

    def to_dict(self):
        return {
            "text": self.text,
            "image": self.image,
            "hashtags": self.hashtags,
            "created_on": self.created_on,
            "views":self.views,
            "likes":self.likes,
            "comments": [comment.dict() for comment in self.comments]
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

# Follow User
@app.put("/follow/{user_id}/")
async def follow_user(user_id: str, target_user_id: str):
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    target_user = user_collection.find_one({"_id": ObjectId(target_user_id)})

    if user and target_user:
        if target_user_id not in user["followed_users"]:
            user["followed_users"].append(target_user_id)
            target_user["followers"].append(user_id)
            
            user_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"followed_users": user["followed_users"]}}
            )
            
            user_collection.update_one(
                {"_id": ObjectId(target_user_id)},
                {"$set": {"followers": target_user["followers"]}}
            )
            return {"message": "User followed successfully"}
        else:
            return {"message": "User is already followed"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

# Unfollow User
@app.put("/unfollow/{user_id}/")
async def unfollow_user(user_id: str, target_user_id: str):
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    target_user = user_collection.find_one({"_id": ObjectId(target_user_id)})

    if user and target_user:
        if target_user_id in user["followed_users"]:
            user["followed_users"].remove(target_user_id)
            target_user["followers"].remove(user_id)
            
            user_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"followed_users": user["followed_users"]}}
            )
            
            user_collection.update_one(
                {"_id": ObjectId(target_user_id)},
                {"$set": {"followers": target_user["followers"]}}
            )
            return {"message": "User unfollowed successfully"}
        else:
            return {"message": "User is not followed"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

# List of Followed Users
@app.get("/user/{user_id}/followed_users/")
async def get_followed_users(user_id: str):
    user = user_collection.find_one({"_id": ObjectId(user_id)})

    if user:
        followed_users = []
        for followed_user_id in user["followed_users"]:
            followed_user = user_collection.find_one({"_id": ObjectId(followed_user_id)})
            if followed_user:
                followed_user["_id"] = str(followed_user["_id"])
                followed_users.append(followed_user)
        return followed_users
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

# Get the discussions by text
@app.get("/discussions/text/")
async def get_discussions_by_text(text: str ):
    discussions = list(discussion_collection.find({"text": {"$regex": text, "$options": "i"}}))
    formatted_discussions = []
    for discussion in discussions:
        discussion["_id"] = str(discussion["_id"])
        formatted_discussions.append(discussion)
    return formatted_discussions

# Add a comment to discussion
@app.put("/discussion/{discussion_id}/comments")
async def add_comment(discussion_id:str,comment:Comment):
    new_comment = comment.dict()
    updated_discussion = discussion_collection.update_one(
        {"_id": ObjectId(discussion_id)},
        {"$push": {"comments": new_comment}}
    )
    if updated_discussion.modified_count == 1:
        return {"message": "Comment added successfully"}
    else:
        raise HTTPException(status_code=404, detail="Discussion not found")


# Like a discussion
@app.patch("/discussion/{discussion_id}/like/")
async def like_discussion(discussion_id: str):
    updated_discussion = discussion_collection.update_one(
        {"_id": ObjectId(discussion_id)},
        {"$inc": {"likes": 1}}
    )
    if updated_discussion.modified_count == 1:
        return {"message": "Discussion liked successfully"}
    else:
        raise HTTPException(status_code=404, detail="Discussion not found")

# Update a comment by index
@app.put("/discussion/{discussion_id}/comments/{comment_index}")
async def update_comment(discussion_id: str, comment_index: int, updated_comment: Comment):
    discussion = discussion_collection.find_one({"_id": ObjectId(discussion_id)})

    if discussion and "comments" in discussion and len(discussion["comments"]) > comment_index:
        updated_comment_dict = updated_comment.dict()
        updated_comment_dict["updated_on"] = datetime.now()
        discussion["comments"][comment_index].update(updated_comment_dict)
        discussion_collection.update_one(
            {"_id": ObjectId(discussion_id)},
            {"$set": {"comments": discussion["comments"]}}
        )
        return {"message": "Comment updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Comment not found")


# Like a comment by index
@app.patch("/discussion/{discussion_id}/comments/{comment_index}/like")
async def like_comment(discussion_id: str, comment_index: int):
    discussion = discussion_collection.find_one({"_id": ObjectId(discussion_id)})
    if discussion and "comments" in discussion and len(discussion["comments"]) > comment_index:
        discussion["comments"][comment_index]["likes"] += 1
        discussion_collection.update_one(
            {"_id": ObjectId(discussion_id)},
            {"$set": {"comments": discussion["comments"]}}
        )
        return {"message": "Comment liked successfully"}
    else:
        raise HTTPException(status_code=404, detail="Comment not found")

# Delete a comment by index
@app.delete("/discussion/{discussion_id}/comments/{comment_index}/delete")
async def delete_comment(discussion_id: str, comment_index: int):
    discussion = discussion_collection.find_one({"_id": ObjectId(discussion_id)})

    if discussion and "comments" in discussion and len(discussion["comments"]) > comment_index:
        discussion["comments"].pop(comment_index)
        discussion_collection.update_one(
            {"_id": ObjectId(discussion_id)},
            {"$set": {"comments": discussion["comments"]}}
        )
        return {"message": "Comment deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Comment not found")

