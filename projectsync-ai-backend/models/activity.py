from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )

    title = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    assigned_to = Column(
        String(200),
        nullable=True
    )

    # Planned Start
    activity_date = Column(
        Date,
        nullable=True
    )

    # Planned End
    planned_end = Column(
        Date,
        nullable=True
    )

    # Actual Start
    actual_start = Column(
        Date,
        nullable=True
    )

    status = Column(
        String(50),
        default="pending",
        nullable=False
    )

    priority = Column(
        String(50),
        default="medium",
        nullable=False
    )