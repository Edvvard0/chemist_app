from fastapi import HTTPException, status


class CustomException(HTTPException):  # <-- наследуемся от HTTPException,
    status_code = 500  # <-- задаем значения по умолчанию
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistsException(CustomException):  # <-- обязательно наследуемся от нашего класса
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь уже существует"


class IncorrectFormatTokenException(CustomException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Не корректный формат токена"


class TokenExpireException(CustomException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен истек"


class IncorrectEmailOrPasswordException(CustomException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Не верный пароль или почта"


class NoPermissionsException(CustomException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Нет доступа"


class UserIsNotPresentException(CustomException):
    status_code = status.HTTP_401_UNAUTHORIZED


class NoTokenException(CustomException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Нет токена"


class UserNotFindException(CustomException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Пользователь не найден"


class ExpiredMedicinesException(CustomException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Просроченный товар"
