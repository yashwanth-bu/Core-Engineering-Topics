#---- Features Included in LEVEL 6 -----
'''
1. Full CRUD operations
2. Filters, pagination, sorting for GET /users
3. JWT authentication with /login
4. Password hashing using bcrypt
5. Role-based access control
6. admin can create/update/delete any user
7. user can only update their own profile via /users/me
8. ObjectId safety and serialization
9. Proper HTTP status codes and validation
10. Production-ready structure
'''

# ----- Project Imports -----
from fastapi import FastAPI, APIRouter, status, HTTPException, Query, Depends, Form
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, validator
from typing import List, Dict, Optional
from pymongo import MongoClient
from bson import ObjectId
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

# ----- App Settings -----
app = FastAPI(title="Pymongo_App", version="1.0.0")

# ----- Database Settings -----
DATABASE_NAME = "mydatabase"
client = MongoClient("mongodb://localhost:27017/")
db = client[DATABASE_NAME]

# ----- JWT Settings -----
SECRET_KEY = "supersecretkey123"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# ----- Helper Functions -----
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def serialize_user(user: dict) -> dict:
    """Convert MongoDB user to safe dict"""
    user["_id"] = str(user["_id"])
    user.pop("password", None)  # remove password
    return user

def validate_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")

# ----- Response Model -----
class ResponseModel(BaseModel):
    message: Optional[str] = None
    response_status: bool = False
    response_data: Optional[List[Dict] | Dict] = None
    total: Optional[int] = None

# ----- User Models -----
class UserCreateModel(BaseModel):
    username: str
    userage: int
    password: str
    role: Optional[str] = "user"

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

    @validator("password")
    def password_length(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

    @validator("role")
    def role_check(cls, v):
        if v not in ("user", "admin"):
            raise ValueError("Role must be 'user' or 'admin'")
        return v

class UserUpdateModel(BaseModel):
    username: Optional[str] = None
    userage: Optional[int] = None
    password: Optional[str] = None
    role: Optional[str] = None

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

    @validator("password")
    def password_length(cls, v):
        if v is not None and len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

    @validator("role")
    def role_check(cls, v):
        if v is not None and v not in ("user", "admin"):
            raise ValueError("Role must be 'user' or 'admin'")
        return v

# ----- JWT Authentication Dependencies -----
def get_current_user(token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    user = db.users.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return serialize_user(user)

def admin_required(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

# ----- Router Initialization -----
user_router = APIRouter(prefix="/users", tags=["Users"])

# ----- Routes -----

# Login route
@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    user = db.users.find_one({"username": username})
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}

# GET all users (public) with filters, pagination, sorting
@user_router.get("/", status_code=status.HTTP_200_OK, response_model=ResponseModel)
def read_all_users(
    username: Optional[str] = Query(None),
    userage: Optional[int] = Query(None),
    limit: int = Query(10),
    skip: int = Query(0),
    sort_by: str = Query("username"),
    sort_order: int = Query(1)
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

# GET user by ID (public)
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

# POST create user (admin only)
@user_router.post("/create", status_code=status.HTTP_201_CREATED, response_model=ResponseModel)
def create_user(body: UserCreateModel, current_user: dict = Depends(admin_required)):
    if db.users.find_one({"username": body.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    user = {
        "username": body.username,
        "userage": body.userage,
        "password": hash_password(body.password),
        "role": body.role
    }
    result = db.users.insert_one(user)
    user["_id"] = str(result.inserted_id)
    user.pop("password")
    return ResponseModel(
        message="User successfully created",
        response_status=True,
        response_data=user
    )

# PUT update user (admin only)
@user_router.put("/{user_id}", status_code=status.HTTP_200_OK, response_model=ResponseModel)
def update_user(user_id: str, body: UserUpdateModel, current_user: dict = Depends(admin_required)):
    user_id_obj = validate_object_id(user_id)
    update_data = {k: (hash_password(v) if k=="password" else v) for k, v in body.dict().items() if v is not None}

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

# DELETE user (admin only)
@user_router.delete("/{user_id}", status_code=status.HTTP_200_OK, response_model=ResponseModel)
def delete_user(user_id: str, current_user: dict = Depends(admin_required)):
    user_id_obj = validate_object_id(user_id)
    result = db.users.delete_one({"_id": user_id_obj})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return ResponseModel(
        message="User successfully deleted",
        response_status=True,
        response_data=None
    )

# PUT update own profile (self)
@user_router.put("/me", status_code=status.HTTP_200_OK, response_model=ResponseModel)
def update_self(body: UserUpdateModel, current_user: dict = Depends(get_current_user)):
    user_id_obj = ObjectId(current_user["_id"])
    update_data = {k: (hash_password(v) if k=="password" else v) for k, v in body.dict().items() if v is not None}

    if not update_data:
        return ResponseModel(
            message="No fields to update",
            response_status=False,
            response_data=None
        )

    db.users.update_one({"_id": user_id_obj}, {"$set": update_data})
    updated_user = db.users.find_one({"_id": user_id_obj})
    return ResponseModel(
        message="Your profile updated successfully",
        response_status=True,
        response_data=serialize_user(updated_user)
    )

# ----- Register Router -----
app.include_router(user_router)