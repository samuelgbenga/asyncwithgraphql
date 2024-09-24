import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from decouple import config

Base = declarative_base()

SQLALCHEMY_DATABASE_URL: str = config("DATABASE_URL") # type: ignore

class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    books = relationship("Book", lazy="joined", back_populates="author")


class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey(Author.id), nullable=True)
    author= relationship(Author, lazy="joined", back_populates="books")


engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL
)

async_session = sessionmaker(
    bind=engine, # type: ignore
    class_=AsyncSession,
    expire_on_commit=False,  # type: ignore
    autoflush=False,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session: # type: ignore
        async with session.begin():
            try:
                yield session
            finally:
                await session.close()


async def _async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


if __name__ == "__main__":
    print("Dropping and creating tables")
    asyncio.run(_async_main())
    print("Done.")