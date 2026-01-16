#---- Features Included in LEVEL 1 -----
'''
1. Full CRUD operations (async)
2. APIRouter usage
3. Pydantic models for request/response
4. Optional fields and default values
5. HTTP status codes
6. Structured JSON response (ResponseModel)
7. Async MongoDB integration with Motor
8. ObjectId usage and safety
9. Type hints and Python typing
10. Basic input validation via Pydantic
'''

# ----- Project Imports -----
from fastapi import FastAPI, status, APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# ----- App Settings -----
app = FastAPI(title="Pymongo_Async_App", version="1.0.0")

# ----- Database Settings -----
DATABASE_NAME = "mydatabase"
MONGO_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client[DATABASE_NAME]

# ----- Models -----
class ResponseModel(BaseModel):
    message: Optional[str] = None
    response_status: bool = False
    response_data: Optional[List[Dict] | Dict] = None

class UserCreateModel(BaseModel):
    username: str
    userage: int

class UserUpdateModel(BaseModel):
    username: Optional[str] = None
    userage: Optional[int] = None

# ----- APIRouter -----
user_router = APIRouter(prefix="/users", tags=["Users"])

# ----- Routes -----

# GET all users
@user_router.get("/", status_code=status.HTTP_200_OK, response_model=ResponseModel)
async def read_all_users():
    users = []
    cursor = db.users.find({})
    async for user in cursor:
        user["_id"] = str(user["_id"])
        users.append(user)
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

    user["_id"] = str(user["_id"])
    return ResponseModel(
        message="User fetched successfully",
        response_status=True,
        response_data=user
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
    updated_user["_id"] = str(updated_user["_id"])
    return ResponseModel(
        message="User updated successfully",
        response_status=True,
        response_data=updated_user
    )

# ----- Include Router -----
app.include_router(user_router)