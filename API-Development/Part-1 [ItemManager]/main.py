from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import uuid
import datetime
import logging

from utils import readJSON, writeJSON

app = FastAPI(
    title="Items API",
    description="CRUD operations for Items",
    version="1.0.0"
)

FILENAME = "Items.json"

# CORS (open for development only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="CRUD-app.log",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

# ------------------ Models ------------------

class ItemCreate(BaseModel):
    item_name: str


class ItemUpdate(BaseModel):
    item_name: Optional[str] = None


class ResponseModel(BaseModel):
    message: str
    response_data: Optional[Dict] = None


# ------------------ Routes ------------------

@app.get(
    "/items",
    status_code=status.HTTP_200_OK,
    response_model=ResponseModel
)
def get_all_items():
    try:
        data = readJSON(FILENAME)
        logger.info("Fetched all items successfully")
        return ResponseModel(
            message="Items fetched successfully",
            response_data=data
        )
    except Exception as e:
        logger.warning(f"Failed to fetch items: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )


@app.post(
    "/items",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseModel
)
def create_item(body: ItemCreate):
    try:
        data = readJSON(FILENAME)

        item_id = str(uuid.uuid4())
        data[item_id] = {
            "item_name": body.item_name,
            "created_time": datetime.datetime.now().isoformat()
        }

        writeJSON(FILENAME, data)
        logger.info(f"Item created successfully - id: {item_id}, name: {body.item_name}")
        return ResponseModel(
            message="Item created successfully",
            response_data={"item_id": item_id}
        )

    except Exception as e:
        logger.warning(f"Failed to create item '{body.item_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )


@app.patch(
    "/items/{item_id}",
    status_code=status.HTTP_200_OK,
    response_model=ResponseModel
)
def update_item(item_id: str, body: ItemUpdate):
    try:
        data = readJSON(FILENAME)

        if item_id not in data:
            logger.warning(f"Update failed - Item not found: {item_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )

        if body.item_name is None:
            logger.warning(f"Update failed - No fields provided for item: {item_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one field must be provided for update"
            )

        data[item_id]["item_name"] = body.item_name
        data[item_id]["updated_time"] = datetime.datetime.now().isoformat()

        writeJSON(FILENAME, data)
        logger.info(f"Item updated successfully - id: {item_id}, new name: {body.item_name}")
        return ResponseModel(message="Item updated successfully")
    
    except HTTPException as e:
        logger.warning(f"HTTPException during update of item {item_id}: {e.detail}")
        raise
    except Exception as e:
        logger.warning(f"Unexpected error updating item {item_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )


@app.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_item(item_id: str):
    try:
        data = readJSON(FILENAME)

        if item_id not in data:
            logger.warning(f"Delete failed - Item not found: {item_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )

        del data[item_id]
        writeJSON(FILENAME, data)
        logger.info(f"Item deleted successfully - id: {item_id}")

    except HTTPException as e:
        logger.warning(f"HTTPException during deletion of item {item_id}: {e.detail}")
        raise
    except Exception as e:
        logger.warning(f"Unexpected error deleting item {item_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )