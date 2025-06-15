from typing import Annotated

from fastapi import Depends
from sqlalchemy import Integer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.config import settings

engine = create_async_engine(url=settings.DB_URL)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)


async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session

        except (SQLAlchemyError, Exception) as e:
            await session.rollback()

            if isinstance(e, SQLAlchemyError):
                msg = "Database"
            else:
                msg = "Unknown"
            msg += " Exp: Cannot add"
            raise e

        finally:
            await session.close()


SessionDep = Annotated[AsyncSession, Depends(get_session)]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    @classmethod
    @property
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"
