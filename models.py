import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

PG_USER = os.getenv("PG_USER", "app")
PG_PASSWORD = os.getenv("PG_PASSWORD", "1234")
PG_DB = os.getenv("PG_DB", "app")
PG_HOST = os.getenv("PG_HOST", "127.0.0.1")
PG_PORT = os.getenv("PG_PORT", 5431)

PG_DSN = f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
TOKEN_TTL = int(os.getenv("TOKEN_TTL", 60 * 60 * 24))

engine = create_async_engine(PG_DSN)

#register(engine.dispose)

Base = declarative_base()
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

class User(Base):
    __table__ = 'owners'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), nullable=False, unique=True)
    user_pass = Column(String(100), nullable=False, unique=True)


class AdModel(Base):
    __tablename__ = 'advertisment'

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    creation_time = Column(DateTime, server_default=func.now())
    owner = Column(String(255), index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey('owners.id', ondelete='CASCADE'), nullable=False)

    owner = relationship(User, cascade='all, delete', backref='advertisments')


#Base.metadata.create_all(engine)