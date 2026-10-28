
from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.sql import func

from database import Base


class WaypointTelemetry(Base):
    __tablename__ = "waypoint_telemetry"

    telemetry_id = Column(Integer, primary_key=True, autoincrement=True)
    drone_id = Column(
        Integer,
        ForeignKey("drone.drone_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reservation_id = Column(
        Integer,
        ForeignKey("reservation.reservation_id", ondelete="SET NULL"),
        nullable=True,
    )
    lat = Column(Numeric(9, 6), nullable=False)
    lon = Column(Numeric(9, 6), nullable=False)
    altitude_m = Column(Numeric(6, 2), nullable=False)
    speed_mps = Column(Numeric(8, 2), nullable=False)
    heading = Column(Numeric(6, 2), nullable=False)
    battery_pct = Column(Numeric(5, 2), nullable=False)
    recorded_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_telemetry_drone_recorded", "drone_id", "recorded_at"),
    )
