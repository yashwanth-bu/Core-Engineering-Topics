#---- Features Included in LEVEL 2 -----
'''
1. ObjectId validation → prevents crashes if user passes invalid ID.
2. _id serialization → converts ObjectId to string for JSON.
3. Error handling → returns proper 404 if user not found.
4. Router consistency → all routes under user_router.
5. Return created user → helpful for POST endpoint.
6. Delete endpoint checks → confirms user existed before deletion.
'''

# ----- Project Imports -----
from fastapi import FastAPI, status, APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from pymongo import MongoClient
from bson import ObjectId

# ----- App Settings -----
app = FastAPI(title="Pymongo_App", version="1.0.0")

# ----- Database -----
DATABASE_NAME = "mydatabase"
client = MongoClient("mongodb://localhost:27017/")
db = client[DATABASE_NAME]

# ----- Models -----
class ResponseModel(BaseModel):
    message: Optional[str] = None
    response_status: bool = False
    response_data : Optional[List[Dict] | Dict] = None

class UserCreateModel(BaseModel):
    username: str
    userage: int

class UserUpdateModel(BaseModel):
    username: Optional[str] = None
    userage: Optional[int] = None

# ----- Router -----
user_router = APIRouter(prefix="/users", tags=["Users"])

# ----- Helper Function -----
def serialize_user(user: dict) -> dict:
    user["_id"] = str(user["_id"])
    return user

# ----- Routes -----
@user_router.get("/", status_code=status.HTTP_200_OK, response_model=ResponseModel)
def read_all_users():
    users = [serialize_user(u) for u in db.users.find({})]
    return ResponseModel(
        message="Users fetched successfully",
        response_status=True,
        response_data=users
    )

@user_router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=ResponseModel)
def read_each_user(user_id: str):
    try:
        user = db.users.find_one({"_id": ObjectId(user_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return ResponseModel(
        message="User fetched successfully",
        response_status=True,
        response_data=serialize_user(user)
    )

@user_router.post("/create", status_code=status.HTTP_201_CREATED, response_model=ResponseModel)
def create_item(body: UserCreateModel):
    user = {"username": body.username, "userage": body.userage}
    result = db.users.insert_one(user)
    user["_id"] = str(result.inserted_id)
    return ResponseModel(
        message="User successfully created",
        response_status=True,
        response_data=user
    )

@user_router.put("/{user_id}", status_code=status.HTTP_200_OK, response_model=ResponseModel)
def update_user(user_id: str, body: UserUpdateModel):
    try:
        ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    update_data = {k: v for k, v in body.dict().items() if v is not None}
    if not update_data:
        return ResponseModel(
            message="No fields to update",
            response_status=False,
            response_data=None
        )

    result = db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = db.users.find_one({"_id": ObjectId(user_id)})
    return ResponseModel(
        message="User updated successfully",
        response_status=True,
        response_data=serialize_user(updated_user)
    )

@user_router.delete("/{user_id}", status_code=status.HTTP_200_OK, response_model=ResponseModel)
def delete_item(user_id: str):
    try:
        result = db.users.delete_one({"_id": ObjectId(user_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return ResponseModel(
        message="User successfully deleted",
        response_status=True,
        response_data=None
    )

# ----- Register Router -----
app.include_router(user_router)