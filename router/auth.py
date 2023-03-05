from datetime import timedelta
from fastapi import APIRouter, Request, Response, status, Depends, HTTPException
import schemas, models, utils, oauth2
from config import settings
from sqlalchemy.orm import Session
from database import get_db
from typing import Any
from oauth2 import AuthJWT
from typing import List


router = APIRouter()
ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN


# Register a new user
@router.post('/user/sign-up', status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
async def create_user(payload: schemas.UserBaseSchema, db: Session = Depends(get_db)) -> Any:
    # Check if user already exist
    user = db.query(models.User).filter(
        models.User.username == payload.username).first()
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Account already exist')
    #  Hash the password
    payload.password = utils.hash_password(payload.password)
    new_user = models.User(**payload.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# Get Token
@router.post('/user/token')
async def get_token(payload: schemas.GetTokenRequest,
                    response: Response,
                    db: Session = Depends(get_db),
                    Authorize: AuthJWT = Depends()):
    # Check if the user exist
    user = db.query(models.User).filter(
              models.User.username == payload.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='User does not exist')

    # Check if the password is valid
    if not utils.verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Incorrect Password')

    # Create access token
    access_token = Authorize.create_access_token(subject=str(user.id),
                                                 expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN))

    # Store and access tokens in cookie
    response.set_cookie('access_token', access_token, ACCESS_TOKEN_EXPIRES_IN * 60,
                        ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')

    # Send both access
    return {'access_token': access_token}


# Get User Profile
@router.get('/user/profile', response_model=schemas.GetMyProfileSchema)
async def get_me(db: Session = Depends(get_db), user_id: str = Depends(oauth2.require_user)):
        user = db.query(models.User).filter(models.User.id == user_id).first()
        return user


# Create a new task
@router.post('/tasks', status_code=status.HTTP_201_CREATED, response_model=schemas.TaskCreateResponse)
async def create_task(payload: schemas.TaskCreateRequest,
                      db: Session = Depends(get_db),
                      user_id: str = Depends(oauth2.require_user)) -> Any:

    user = db.query(models.User).filter(models.User.id == user_id).first()
    payload_dict = payload.dict()
    payload_dict.update({"user_id": user.id})
    new_task = models.Task(**payload_dict)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


# Get All User's Tasks
@router.get('/tasks', response_model=List[schemas.AllTasksResponse])
async def get_all_tasks(db: Session = Depends(get_db), user_id: str = Depends(oauth2.require_user)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    user_tasks = db.query(models.Task).filter(models.Task.user_id == user.id).all()
    return user_tasks


# Get User' Task By Id
@router.get('/tasks/{id}', response_model=schemas.AllTasksResponse)
async def get_all_tasks(id: int,
                        db: Session = Depends(get_db),
                        user_id: str = Depends(oauth2.require_user)):
    task = db.query(models.Task).filter(models.Task.id == id).first()
    return task