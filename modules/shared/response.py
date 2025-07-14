from fastapi.responses import JSONResponse

def success_response(data, status_code=200):
    return JSONResponse(status_code=status_code, content={"status": "success", "data": data})

def error_response(message, status_code=400):
    return JSONResponse(status_code=status_code, content={"status": "error", "message": message})