from datetime import datetime
import uuid
from pydantic import BaseModel, EmailStr, constr


# Login request (UserBase)
class UserBaseSchema(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str

    class Config:
        orm_mode = True


# Login Response
class UserResponse(BaseModel):
    id: uuid.UUID

    class Config:
        orm_mode = True


# Token Request
class GetTokenRequest(BaseModel):
    username: str
    password: str

    class Config:
        orm_mode = True


# Get My Profile Response (UserBase)
class GetMyProfileSchema(UserBaseSchema):
    id: uuid.UUID

    class Config:
        orm_mode = True


# Task Create Request
class TaskCreateRequest(BaseModel):
    title: str

    class Config:
        orm_mode = True


# Task Create Response
class TaskCreateResponse(BaseModel):
    id: int

    class Config:
        orm_mode = True


# Get All Tasks Response
class AllTasksResponse(TaskCreateResponse):
    title: str
    created_at: datetime
    user_id: uuid.UUID

    class Config:
        orm_mode = True







