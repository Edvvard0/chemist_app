from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import selectinload
from starlette import status
from starlette.responses import Response

from app.database import SessionDep
from app.exception import IncorrectEmailOrPasswordException
from app.users.auth import authenticate_user, create_access_token, get_password_hash
from app.users.dao import UserDAO
from app.users.dependensies import get_current_user
from app.users.models import User
from app.users.schemas import SUser, SUserAdd, SUserLogin

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/login")
async def login_user(response: Response,session: SessionDep, user_data: SUserLogin):
    user = await authenticate_user(user_data.email, user_data.password, session)
    if not user:
        raise IncorrectEmailOrPasswordException
    access_token = create_access_token({'sub': str(user.id)})
    response.set_cookie("access_token", access_token, httponly=True)
    return access_token


@router.post("/")
async def add_user(session: SessionDep, user: SUserAdd):
    user = user.model_dump()
    user["password"] = get_password_hash(user["password"])
    await UserDAO.add(session=session, **user)
    return {"message": "User add"}


@router.get("/{user_id}")
async def get_user(session: SessionDep, user_id: int) -> SUser:
    user = await UserDAO.find_one_or_none_by_id(session=session, model_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с таким id не найден"
            )
    return user


@router.delete("/{user_id}")
async def delete_user(session: SessionDep, user_id: int):
    await UserDAO.delete(session, id=user_id)
