#---- Features Included in LEVEL 1 -----
'''
1. Full CRUD operations
2. Basic APIRouter usage
3. Pydantic models for request and response
4. Optional fields and default values
5. HTTP status codes for responses
6. Structured JSON response
7. MongoDB integration with PyMongo
8. ObjectId usage
9. Type hints and Python typing
10. Basic input validation via Pydantic
'''

# ----- Project Imports -----
from fastapi import FastAPI, status, APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from pymongo import MongoClient
from bson import ObjectId

# ----- App Settings -----
app = FastAPI(title="Pymongo_App", version="1.0.0")


# ----- Database Settings -----
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
    

# ----- Routers initation -----
user_router = APIRouter(prefix="/users", tags=["Users"])


# -----  Users router specifing -----
@user_router.get("/", status_code=status.HTTP_200_OK, response_model=ResponseModel)
def read_all_users():
    users = []
    for user in db.users.find({}):
        user["_id"] = str(user["_id"])
        users.append(user)

    return ResponseModel(
        message="Users fetched successfully",
        response_status=True,
        response_data=users
    )
    
@user_router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=ResponseModel)
def read_each_user(user_id: str):
    user = db.users.find_one({"_id": ObjectId(user_id)})
    user["_id"] = str(user["_id"])
    return ResponseModel(
        message="User fetched successfully",
        response_status=True,
        response_data=user
    )

@user_router.post("/create", status_code=status.HTTP_201_CREATED, response_model=ResponseModel)
def create_item(body: UserCreateModel):
    user = {"username": body.username, "userage": body.userage}
    result = db.users.insert_one(user)

    return ResponseModel(
        message=f"User successfully created with ID-{str(result.inserted_id)}",
        response_status=True,
        response_data=None
    )
    
@user_router.delete("/{user_id}", status_code=status.HTTP_200_OK, response_model=ResponseModel)
def delete_item(user_id: str):
    db.users.delete_one({"_id":  ObjectId(user_id)})
    return ResponseModel(
        message="User successfully Delted",
        response_status=True,
        response_data=None
    )


@app.put("/{user_id}", status_code=200, response_model=ResponseModel)
def update_user(user_id: str, body: UserUpdateModel):

    update_data = {k: v for k, v in body.dict().items() if v is not None}

    if not update_data:
        return ResponseModel(
            message="No fields to update",
            response_status=False,
            response_data=None
        )

    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )

    updated_user = db.users.find_one({"_id": ObjectId(user_id)})

    return ResponseModel(
        message="User updated successfully",
        response_status=True,
        response_data=updated_user
    )

# ----- Routers declaration -----
app.include_router(user_router)