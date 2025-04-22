from sqlalchemy import Column, Integer, Float, String, DateTime
from database import Base
from datetime import datetime

class Telemetria(Base):
    __tablename__ = "telemetria"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    accX = Column(Float)
    accY = Column(Float)
    accZ = Column(Float)
    temp = Column(Float)
    alt = Column(Float)
    comentario = Column(String, nullable=True)
