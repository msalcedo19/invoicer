from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from ms_invoicer.config import URL_CONNECTION

engine = create_engine(URL_CONNECTION, pool_size=15, max_overflow=25)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
