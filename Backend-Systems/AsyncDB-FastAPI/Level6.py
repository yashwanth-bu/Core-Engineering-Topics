#---- Features Included in LEVEL 6 -----
'''
1. Async Motor CRUD
2. JWT authentication
3. Password hashing (bcrypt)
4. Role-based access control (admin vs user)
5. Filters, pagination, sorting for GET /users
6. Proper HTTP status codes and validation
7. Secure password handling (never exposed)
8. Clean serialization of ObjectId
9. Production-ready route structure
'''


# ----- Project Imports -----
from fastapi import FastAPI, status, APIRouter, HTTPException, Depends, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Dict, Optional, Union
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

# ----- App Settings -----
app = FastAPI(title="Pymongo_Async_App", version="5.0.0")

# ----- Database Settings -----
DATABASE_NAME = "mydatabase"
MONGO_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client[DATABASE_NAME]

# ----- JWT Settings -----
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ----- Password Hashing -----
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ----- Models -----
class ResponseModel(BaseModel):
    message: Optional[str] = None
    response_status: bool = False
    response_data: Optional[Union[List[Dict], Dict]] = None

class UserCreateModel(BaseModel):
    username: str
    password: str
    userage: int
    role: Optional[str] = "user"

class UserUpdateModel(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    userage: Optional[int] = None

class Token(BaseModel):
    access_token: str
    token_type: str

# ----- APIRouter -----
user_router = APIRouter(prefix="/users", tags=["Users"])

# ----- Utilities -----
def serialize_user(user: Dict) -> Dict:
    user["_id"] = str(user["_id"])
    if "password" in user:
        del user["password"]
    return user

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

def require_admin(user: dict):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return True

# ----- Routes -----

# POST create user (admin only)
@user_router.post("/create", status_code=status.HTTP_201_CREATED, response_model=ResponseModel)
async def create_user(body: UserCreateModel, current_user: dict = Depends(get_current_user)):
    require_admin(current_user)
    hashed_password = hash_password(body.password)
    user = {"username": body.username, "password": hashed_password, "userage": body.userage, "role": body.role}
    result = await db.users.insert_one(user)
    return ResponseModel(
        message=f"User successfully created with ID-{str(result.inserted_id)}",
        response_status=True
    )

# POST login
@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await db.users.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token(
        data={"sub": str(user["_id"]), "role": user.get("role")},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# GET all users (admin only, with filters, pagination, sorting)
@user_router.get("/", status_code=status.HTTP_200_OK, response_model=ResponseModel)
async def read_all_users(
    username: Optional[str] = Query(None),
    min_age: Optional[int] = Query(None),
    max_age: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    sort_by: str = Query("username"),
    sort_order: str = Query("asc"),
    current_user: dict = Depends(get_current_user)
):
    require_admin(current_user)
    query = {}
    if username:
        query["username"] = {"$regex": username, "$options": "i"}
    if min_age is not None or max_age is not None:
        query["userage"] = {}
        if min_age is not None:
            query["userage"]["$gte"] = min_age
        if max_age is not None:
            query["userage"]["$lte"] = max_age
    sort_dir = 1 if sort_order.lower() == "asc" else -1
    users = []
    cursor = db.users.find(query).sort(sort_by, sort_dir).skip(skip).limit(limit)
    async for user in cursor:
        users.append(serialize_user(user))
    return ResponseModel(
        message="Users fetched successfully",
        response_status=True,
        response_data=users
    )

# GET single user (self or admin)
@user_router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=ResponseModel)
async def read_each_user(user_id: str, current_user: dict = Depends(get_current_user)):
    try:
        user_obj_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    user = await db.users.find_one({"_id": user_obj_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.get("role") != "admin" and str(user["_id"]) != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to view this user")
    return ResponseModel(
        message="User fetched successfully",
        response_status=True,
        response_data=serialize_user(user)
    )

# PUT update user (self or admin)
@user_router.put("/{user_id}", status_code=status.HTTP_200_OK, response_model=ResponseModel)
async def update_user(user_id: str, body: UserUpdateModel, current_user: dict = Depends(get_current_user)):
    try:
        user_obj_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    update_data = {k: v for k, v in body.dict().items() if v is not None}
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])
    if not update_data:
        return ResponseModel(message="No fields to update", response_status=False)
    if current_user.get("role") != "admin" and str(user_obj_id) != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    result = await db.users.update_one({"_id": user_obj_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = await db.users.find_one({"_id": user_obj_id})
    return ResponseModel(
        message="User updated successfully",
        response_status=True,
        response_data=serialize_user(updated_user)
    )

# DELETE user (admin only)
@user_router.delete("/{user_id}", status_code=status.HTTP_200_OK, response_model=ResponseModel)
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    require_admin(current_user)
    try:
        user_obj_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    result = await db.users.delete_one({"_id": user_obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return ResponseModel(message="User successfully deleted", response_status=True)

# ----- Include Router -----
app.include_router(user_router)