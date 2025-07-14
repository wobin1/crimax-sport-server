from pydantic import BaseModel, EmailStr, validator

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str

    @validator("role")
    def validate_role(cls, value):
        valid_roles = {"admin", "team_manager", "player", "guest"}
        if value not in valid_roles:
            raise ValueError(f"Role must be one of {valid_roles}")
        return value

class UserLogin(BaseModel):
    username: str
    password: str