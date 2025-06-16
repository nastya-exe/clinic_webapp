from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL




engine = create_async_engine(DATABASE_URL, echo=True)

async_session_maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

