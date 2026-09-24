
from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from database import Base


class DailyReport(Base):
    __tablename__ = "daily_reports"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )

    report_date = Column(
        Date,
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

    submitted_by = Column(
        String(200),
        nullable=True
    )

    status = Column(
        String(50),
        default="submitted"
    )

    file_name = Column(
        String(255),
        nullable=True
    )

    file_path = Column(
        String(500),
        nullable=True
    )
