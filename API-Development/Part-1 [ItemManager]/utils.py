import json
from fastapi import HTTPException


def readJSON(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied to read the file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


def writeJSON(filename, new_data):
    try:
        with open(filename, 'w') as file:
            json.dump(new_data, file, indent=4)
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied to write the file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")