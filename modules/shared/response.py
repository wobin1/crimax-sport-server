from fastapi.responses import JSONResponse
from datetime import datetime, date
import json

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

def serialize_data(data):
    """Recursively serialize data, converting datetime objects to ISO format strings"""
    if isinstance(data, dict):
        return {key: serialize_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [serialize_data(item) for item in data]
    elif isinstance(data, (datetime, date)):
        return data.isoformat()
    return data

def success_response(data, status_code=200):
    serialized_data = serialize_data(data)
    return JSONResponse(status_code=status_code, content={"status": "success", "data": serialized_data})

def error_response(message, status_code=400):
    return JSONResponse(status_code=status_code, content={"status": "error", "message": message})