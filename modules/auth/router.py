import logging
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordBearer
from .manager import register_user, authenticate_user, create_access_token, blacklist_token
from .models import UserCreate, UserLogin
from modules.shared.response import success_response, error_response

logger = logging.getLogger("auth_router")

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    logger.debug(f"Authenticating user with token: {token}")
    user = await authenticate_user(token=token)
    if not user:
        logger.warning("Invalid or expired token provided.")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    logger.info(f"Authenticated user: {user.get('username', 'unknown')}")
    return user

@router.post("/register")
async def register(user: UserCreate):
    logger.info(f"Attempting to register user: {user.username}")
    user_id = await register_user(user)
    if not user_id:
        logger.warning(f"Registration failed for user: {user.username} (username or email exists)")
        return error_response("Username or email already exists", 400)
    logger.info(f"User registered successfully: {user.username} (user_id: {user_id})")
    return success_response({"user_id": user_id}, 201)

@router.post("/login")
async def login(user: UserLogin, response: Response):
    logger.info(f"Login attempt for user: {user.username}")
    user_data = await authenticate_user(username=user.username, password=user.password)
    if not user_data:
        logger.warning(f"Login failed for user: {user.username} (invalid credentials)")
        return error_response("Invalid credentials", 401)
    token = create_access_token({"sub": user_data["username"], "role": user_data["role"]})
    logger.info(f"User {user.username} logged in successfully. Token generated.")
    response.set_cookie(key="access_token", value=token, httponly=True, secure=True)
    return success_response({"access_token": token, "token_type": "bearer"})

@router.post("/logout", dependencies=[Depends(get_current_user)])
async def logout(response: Response, token: str = Depends(oauth2_scheme)):
    logger.info(f"Logout attempt with token: {token}")
    await blacklist_token(token)  # Add token to blacklist
    response.delete_cookie(key="access_token")
    logger.info("User logged out successfully and token blacklisted.")
    return success_response({"message": "Logged out successfully"})

@router.get("/me", dependencies=[Depends(get_current_user)])
async def get_me(current_user: dict = Depends(get_current_user)):
    logger.debug(f"Fetching current user info: {current_user.get('username', 'unknown')}")
    return success_response(current_user)