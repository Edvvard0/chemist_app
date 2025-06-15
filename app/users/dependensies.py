from datetime import datetime

from fastapi import Request, HTTPException, status, Depends
from jose import jwt, JWTError

from app.config import settings
from app.database import SessionDep
from app.exception import IncorrectFormatTokenException, TokenExpireException, NoPermissionsException, \
    UserIsNotPresentException, NoTokenException

from app.users.dao import UserDAO


def get_token(request: Request):
    token = request.cookies.get('access_token')
    if not token:
        raise NoTokenException
    return token


async def get_current_user(session: SessionDep, token: str = Depends(get_token)):
    try:
        payload = jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise IncorrectFormatTokenException

    expire: str = payload.get('exp')
    if (not expire) or (int(expire) < datetime.utcnow().timestamp()):
        raise TokenExpireException

    user_id: str = payload.get('sub')
    if not user_id:
        raise UserIsNotPresentException

    user = await UserDAO.find_one_or_none_by_id(session, int(user_id))
    if not user:
        raise UserIsNotPresentException

    return user