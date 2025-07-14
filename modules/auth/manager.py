import jwt
import bcrypt
import logging
from datetime import datetime, timedelta
from modules.shared.db import get_db_connection
from .models import UserCreate

logger = logging.getLogger("auth_manager")

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

async def register_user(user: UserCreate):
    logger.debug(f"Attempting to register user: username={user.username}, email={user.email}, role={user.role}")
    conn = await get_db_connection()
    try:
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        logger.debug("Password hashed successfully for user registration.")
        existing = await conn.fetchrow(
            "SELECT user_id FROM users WHERE username = $1 OR email = $2", user.username, user.email
        )
        if existing:
            logger.info(f"Registration failed: Username or email already exists for username={user.username}, email={user.email}")
            return None
        user_id = await conn.fetchval("""
            INSERT INTO users (username, email, password, role)
            VALUES ($1, $2, $3, $4) RETURNING user_id
        """, user.username, user.email, hashed_password, user.role)
        logger.info(f"User registered successfully: username={user.username}, user_id={user_id}")
        return user_id
    except Exception as e:
        logger.error(f"Error during user registration: {e}", exc_info=True)
        raise
    finally:
        await conn.close()
        logger.debug("Database connection closed after register_user.")

async def authenticate_user(username: str = None, password: str = None, token: str = None):
    logger.debug(f"Authenticating user. username={username}, token={'provided' if token else 'not provided'}")
    conn = await get_db_connection()
    try:
        if token:  # Authenticate via token
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                username = payload.get("sub")
                logger.debug(f"Decoded JWT token. Username from token: {username}")
                if username is None:
                    logger.warning("JWT token does not contain 'sub' (username).")
                    return None
                if await is_token_blacklisted(token):
                    logger.warning("Token is blacklisted.")
                    return None
            except jwt.ExpiredSignatureError:
                logger.warning("JWT token has expired.")
                return None
            except jwt.InvalidTokenError as e:
                logger.warning(f"Invalid JWT token: {e}")
                return None
            user = await conn.fetchrow(
                "SELECT user_id, username, email, role FROM users WHERE username = $1", username
            )
            if user:
                logger.info(f"User authenticated via token: {username}")
            else:
                logger.warning(f"No user found for username from token: {username}")
            return dict(user) if user else None
        else:  # Authenticate via username/password
            user = await conn.fetchrow(
                "SELECT user_id, username, email, password, role FROM users WHERE username = $1", username
            )
            if not user:
                logger.warning(f"Authentication failed: No user found with username={username}")
                return None
            if not bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
                logger.warning(f"Authentication failed: Incorrect password for username={username}")
                return None
            logger.info(f"User authenticated via username/password: {username}")
            return {k: user[k] for k in ("user_id", "username", "email", "role")}
    except Exception as e:
        logger.error(f"Error during authentication: {e}", exc_info=True)
        raise
    finally:
        await conn.close()
        logger.debug("Database connection closed after authenticate_user.")

def create_access_token(data: dict):
    logger.debug(f"Creating access token for data: {data}")
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Access token created. Expires at: {expire.isoformat()}")
    return token

async def blacklist_token(token: str):
    logger.debug("Blacklisting token.")
    conn = await get_db_connection()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expires_at = datetime.fromtimestamp(payload["exp"])
        await conn.execute("""
            INSERT INTO token_blacklist (token, expires_at)
            VALUES ($1, $2)
            ON CONFLICT (token) DO NOTHING
        """, token, expires_at)
        logger.info(f"Token blacklisted until {expires_at.isoformat()}")
    except Exception as e:
        logger.error(f"Error blacklisting token: {e}", exc_info=True)
        raise
    finally:
        await conn.close()
        logger.debug("Database connection closed after blacklist_token.")

async def is_token_blacklisted(token: str):
    logger.debug("Checking if token is blacklisted.")
    conn = await get_db_connection()
    try:
        result = await conn.fetchrow(
            "SELECT EXISTS (SELECT 1 FROM token_blacklist WHERE token = $1 AND expires_at > NOW())",
            token
        )
        is_blacklisted = result["exists"]
        logger.debug(f"Token blacklisted: {is_blacklisted}")
        return is_blacklisted
    except Exception as e:
        logger.error(f"Error checking token blacklist: {e}", exc_info=True)
        raise
    finally:
        await conn.close()
        logger.debug("Database connection closed after is_token_blacklisted.")