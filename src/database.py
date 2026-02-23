from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# 1. SQLite DB 파일 위치 설정 (프로젝트 최상단에 optiserve.db 생성)
SQLALCHEMY_DATABASE_URL = "sqlite:///./optiserve.db"

# 2. DB 엔진 및 세션 생성
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 3. 로그 테이블(Table) 스키마 정의
class UserLog(Base):
    __tablename__ = "user_logs"

    id = Column(Integer, primary_key=True, index=True)     # 고유 번호
    user_id = Column(String, index=True)                   # 유저 ID
    ab_group = Column(String)                              # A군인지 B군인지
    item_name = Column(String)                             # 추천/클릭된 상품명
    action_type = Column(String)                           # 행동 유형 ("impression" 또는 "click")
    timestamp = Column(DateTime, default=datetime.utcnow)  # 행동이 일어난 시간