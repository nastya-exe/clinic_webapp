import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(os.path.join(__file__, '..', '..'))))

from config import DATABASE_URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()
