
from fastapi import APIRouter, Depends, HTTPException, Query
from redis import Redis
from sqlalchemy.orm import Session

from database import get_db
from modules.fleet.models import Drone
from modules.telemetry.models import WaypointTelemetry
from modules.telemetry.schemas import TelemetryData
from modules.telemetry.websocket import broadcast_telemetry

telemetry_router = APIRouter(
    prefix="/api/telemetry",
    tags=["telemetry"],
)

redis_client = Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
)


@telemetry_router.post("")
async def receive_telemetry(
    data: TelemetryData,
    db: Session = Depends(get_db),
):
    try:
        drone_id = int(data.drone_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=422,
            detail="drone_id must be an integer",
        )

    drone = db.query(Drone).filter(
        Drone.drone_id == drone_id
    ).first()

    if drone is None:
        raise HTTPException(
            status_code=404,
            detail="Drone not found",
        )

    telemetry = {
        "drone_id": str(drone_id),
        "latitude": data.latitude,
        "longitude": data.longitude,
        "altitude_m": data.altitude_m,
        "speed_mps": data.speed_mps,
        "heading": data.heading,
        "battery_pct": data.battery_pct,
        "timestamp": data.timestamp.isoformat(),
    }

    record = WaypointTelemetry(
        drone_id=drone_id,
        lat=data.latitude,
        lon=data.longitude,
        altitude_m=data.altitude_m,
        speed_mps=data.speed_mps,
        heading=data.heading,
        battery_pct=data.battery_pct,
        recorded_at=data.timestamp,
    )

    try:
        db.add(record)
        db.commit()
        db.refresh(record)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to save telemetry history",
        )

    try:
        redis_client.hset(
            f"telemetry:{drone_id}",
            mapping=telemetry,
        )
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Telemetry saved to history, but Redis update failed",
        )

    await broadcast_telemetry(telemetry)

    return {
        "status": "received",
        "drone_id": drone_id,
        "telemetry_id": record.telemetry_id,
    }


@telemetry_router.get("/{drone_id}/history")
def get_telemetry_history(
    drone_id: int,
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    drone = db.query(Drone).filter(
        Drone.drone_id == drone_id
    ).first()

    if drone is None:
        raise HTTPException(
            status_code=404,
            detail="Drone not found",
        )

    records = (
        db.query(WaypointTelemetry)
        .filter(WaypointTelemetry.drone_id == drone_id)
        .order_by(WaypointTelemetry.recorded_at.asc())
        .limit(limit)
        .all()
    )

    return {
        "drone_id": drone_id,
        "count": len(records),
        "history": [
            {
                "telemetry_id": record.telemetry_id,
                "drone_id": record.drone_id,
                "latitude": float(record.lat),
                "longitude": float(record.lon),
                "altitude_m": float(record.altitude_m),
                "speed_mps": float(record.speed_mps),
                "heading": float(record.heading),
                "battery_pct": float(record.battery_pct),
                "timestamp": record.recorded_at.isoformat(),
            }
            for record in records
        ],
    }


@telemetry_router.get("/{drone_id}")
def get_latest_telemetry(drone_id: str):
    data = redis_client.hgetall(f"telemetry:{drone_id}")

    if not data:
        return {
            "status": "not_found",
            "drone_id": drone_id,
        }

    return data
