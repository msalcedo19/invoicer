from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from ms_invoicer.config import URL_CONNECTION

engine = create_engine(URL_CONNECTION)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
