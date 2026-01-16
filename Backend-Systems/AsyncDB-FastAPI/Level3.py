#---- Features Included in LEVEL 3 -----
'''
1. Filtering by username (partial, case-insensitive) and age range
2. Pagination using skip and limit
3. Sorting by any field (username or userage) in ascending/descending order
4. All routes remain async with Motor
5. Responses remain consistent and serialized
'''


# ----- Project Imports -----
from fastapi import FastAPI, status, APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional, Union
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# ----- App Settings -----
app = FastAPI(title="Pymongo_Async_App", version="2.0.0")

# ----- Database Settings -----
DATABASE_NAME = "mydatabase"
MONGO_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client[DATABASE_NAME]

# ----- Models -----
class ResponseModel(BaseModel):
    message: Optional[str] = None
    response_status: bool = False
    response_data: Optional[Union[List[Dict], Dict]] = None

class UserCreateModel(BaseModel):
    username: str
    userage: int

class UserUpdateModel(BaseModel):
    username: Optional[str] = None
    userage: Optional[int] = None

# ----- APIRouter -----
user_router = APIRouter(prefix="/users", tags=["Users"])

# ----- Utility Function for ObjectId Serialization -----
def serialize_user(user: Dict) -> Dict:
    user["_id"] = str(user["_id"])
    return user

# ----- Routes -----

# GET all users with filters, pagination, sorting
@user_router.get("/", status_code=status.HTTP_200_OK, response_model=ResponseModel)
async def read_all_users(
    username: Optional[str] = Query(None, description="Filter by username"),
    min_age: Optional[int] = Query(None, description="Filter by minimum age"),
    max_age: Optional[int] = Query(None, description="Filter by maximum age"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, description="Maximum number of records to return"),
    sort_by: Optional[str] = Query("username", description="Field to sort by"),
    sort_order: Optional[str] = Query("asc", description="Sort order: asc or desc")
):
    query = {}
    if username:
        query["username"] = {"$regex": username, "$options": "i"}  # case-insensitive
    if min_age is not None or max_age is not None:
        query["userage"] = {}
        if min_age is not None:
            query["userage"]["$gte"] = min_age
        if max_age is not None:
            query["userage"]["$lte"] = max_age

    sort_direction = 1 if sort_order.lower() == "asc" else -1

    users = []
    cursor = db.users.find(query).sort(sort_by, sort_direction).skip(skip).limit(limit)
    async for user in cursor:
        users.append(serialize_user(user))

    return ResponseModel(
        message="Users fetched successfully",
        response_status=True,
        response_data=users
    )

# GET single user
@user_router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=ResponseModel)
async def read_each_user(user_id: str):
    try:
        user_obj_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    user = await db.users.find_one({"_id": user_obj_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return ResponseModel(
        message="User fetched successfully",
        response_status=True,
        response_data=serialize_user(user)
    )

# POST create user
@user_router.post("/create", status_code=status.HTTP_201_CREATED, response_model=ResponseModel)
async def create_user(body: UserCreateModel):
    user = {"username": body.username, "userage": body.userage}
    result = await db.users.insert_one(user)
    return ResponseModel(
        message=f"User successfully created with ID-{str(result.inserted_id)}",
        response_status=True,
        response_data=None
    )

# DELETE user
@user_router.delete("/{user_id}", status_code=status.HTTP_200_OK, response_model=ResponseModel)
async def delete_user(user_id: str):
    try:
        user_obj_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    result = await db.users.delete_one({"_id": user_obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return ResponseModel(
        message="User successfully deleted",
        response_status=True,
        response_data=None
    )

# PUT update user
@user_router.put("/{user_id}", status_code=status.HTTP_200_OK, response_model=ResponseModel)
async def update_user(user_id: str, body: UserUpdateModel):
    try:
        user_obj_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    update_data = {k: v for k, v in body.dict().items() if v is not None}
    if not update_data:
        return ResponseModel(
            message="No fields to update",
            response_status=False,
            response_data=None
        )

    result = await db.users.update_one({"_id": user_obj_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = await db.users.find_one({"_id": user_obj_id})
    return ResponseModel(
        message="User updated successfully",
        response_status=True,
        response_data=serialize_user(updated_user)
    )

# ----- Include Router -----
app.include_router(user_router)