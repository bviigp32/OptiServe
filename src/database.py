from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./optiserve.db" 
)

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL) # PostgreSQL 등 RDBMS용

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserLog(Base):
    __tablename__ = "user_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    ab_group = Column(String, index=True)     # "A" 또는 "B"
    item_name = Column(String)                # 추천된/클릭된 아이템 이름
    action_type = Column(String, index=True)  # "impression" (노출) 또는 "click" (클릭)
    timestamp = Column(DateTime, default=datetime.utcnow)