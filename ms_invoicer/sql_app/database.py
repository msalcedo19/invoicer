from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from ms_invoicer.config import URL_CONNECTION

engine = create_engine(URL_CONNECTION, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
