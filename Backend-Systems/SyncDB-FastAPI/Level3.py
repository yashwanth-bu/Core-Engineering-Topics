#---- Features Included in LEVEL 3 -----
'''
1. CRUD operations (GET all, GET by ID, POST, PUT, DELETE)
2. ObjectId validation → avoids crashes on invalid IDs
3. _id serialization → converts ObjectId to string
4. Filters on GET /users → username, userage
5. Pagination → limit and skip
6. Sorting → sort_by and sort_order
7. Input validation → username min length, positive age
8. Proper HTTP status codes → 200, 201, 400, 404
9. Optional total count → useful for frontend pagination
'''

# ----- Project Imports -----
from fastapi import FastAPI, APIRouter, status, HTTPException, Query
from pydantic import BaseModel, validator
from typing import List, Dict, Optional
from pymongo import MongoClient
from bson import ObjectId

# ----- App Settings -----
app = FastAPI(title="Pymongo_App", version="1.0.0")

# ----- Database Settings -----
DATABASE_NAME = "mydatabase"
client = MongoClient("mongodb://localhost:27017/")
db = client[DATABASE_NAME]

# ----- Helper Functions -----
def serialize_user(user: dict) -> dict:
    """Convert MongoDB ObjectId to string"""
    user["_id"] = str(user["_id"])
    return user

def validate_object_id(id_str: str) -> ObjectId:
    """Check if string is a valid ObjectId"""
    try:
        return ObjectId(id_str)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")

# ----- Response Model -----
class ResponseModel(BaseModel):
    message: Optional[str] = None
    response_status: bool = False
    response_data: Optional[List[Dict] | Dict] = None
    total: Optional[int] = None  # Optional total count for pagination

# ----- User Models -----
class UserCreateModel(BaseModel):
    username: str
    userage: int

    @validator("username")
    def username_length(cls, v):
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v

    @validator("userage")
    def age_positive(cls, v):
        if v <= 0:
            raise ValueError("User age must be positive")
        return v

class UserUpdateModel(BaseModel):
    username: Optional[str] = None
    userage: Optional[int] = None

    @validator("username")
    def username_length(cls, v):
        if v is not None and len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v

    @validator("userage")
    def age_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("User age must be positive")
        return v

# ----- Router Initialization -----
user_router = APIRouter(prefix="/users", tags=["Users"])

# ----- Routes -----

# GET all users with optional filters, pagination, sorting
@user_router.get("/", status_code=status.HTTP_200_OK, response_model=ResponseModel)
def read_all_users(
    username: Optional[str] = Query(None, description="Filter by username"),
    userage: Optional[int] = Query(None, description="Filter by age"),
    limit: int = Query(10, description="Number of users to return"),
    skip: int = Query(0, description="Number of users to skip"),
    sort_by: str = Query("username", description="Field to sort by"),
    sort_order: int = Query(1, description="1=ascending, -1=descending")
):
    query = {}
    if username:
        query["username"] = {"$regex": username, "$options": "i"}
    if userage is not None:
        query["userage"] = userage

    total = db.users.count_documents(query)
    users_cursor = db.users.find(query).skip(skip).limit(limit).sort(sort_by, sort_order)
    users = [serialize_user(u) for u in users_cursor]

    return ResponseModel(
        message="Users fetched successfully",
        response_status=True,
        response_data=users,
        total=total
    )

# GET single user by ID
@user_router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=ResponseModel)
def read_each_user(user_id: str):
    user_id_obj = validate_object_id(user_id)
    user = db.users.find_one({"_id": user_id_obj})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return ResponseModel(
        message="User fetched successfully",
        response_status=True,
        response_data=serialize_user(user)
    )

# POST create new user
@user_router.post("/create", status_code=status.HTTP_201_CREATED, response_model=ResponseModel)
def create_user(body: UserCreateModel):
    user = {"username": body.username, "userage": body.userage}
    result = db.users.insert_one(user)
    user["_id"] = str(result.inserted_id)
    return ResponseModel(
        message="User successfully created",
        response_status=True,
        response_data=user
    )

# PUT update existing user
@user_router.put("/{user_id}", status_code=status.HTTP_200_OK, response_model=ResponseModel)
def update_user(user_id: str, body: UserUpdateModel):
    user_id_obj = validate_object_id(user_id)
    update_data = {k: v for k, v in body.dict().items() if v is not None}

    if not update_data:
        return ResponseModel(
            message="No fields to update",
            response_status=False,
            response_data=None
        )

    result = db.users.update_one({"_id": user_id_obj}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = db.users.find_one({"_id": user_id_obj})
    return ResponseModel(
        message="User updated successfully",
        response_status=True,
        response_data=serialize_user(updated_user)
    )

# DELETE user
@user_router.delete("/{user_id}", status_code=status.HTTP_200_OK, response_model=ResponseModel)
def delete_user(user_id: str):
    user_id_obj = validate_object_id(user_id)
    result = db.users.delete_one({"_id": user_id_obj})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return ResponseModel(
        message="User successfully deleted",
        response_status=True,
        response_data=None
    )

# ----- Register Router -----
app.include_router(user_router)