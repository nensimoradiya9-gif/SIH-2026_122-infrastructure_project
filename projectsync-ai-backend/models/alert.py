from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)

    severity = Column(
        String(50),
        nullable=False,
        default="info"
    )

    message = Column(
        Text,
        nullable=False
    )

    time_label = Column(
        String(100),
        nullable=True
    )

    status = Column(
        String(50),
        nullable=False,
        default="unread"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )