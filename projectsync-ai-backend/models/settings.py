from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from database import Base


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    theme = Column(String(50), default="light")
    notifications_enabled = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)