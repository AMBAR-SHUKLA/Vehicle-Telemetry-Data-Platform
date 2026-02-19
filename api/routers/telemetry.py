"""
Telemetry Data Ingestion API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from database.models import Telemetry as TelemetryModel, Vehicle as VehicleModel, get_db
from api.schemas import Telemetry, TelemetryCreate

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/telemetry",
    tags=["telemetry"],
    responses={404: {"description": "Not found"}}
)


@router.post("/", response_model=Telemetry, status_code=status.HTTP_201_CREATED)
async def ingest_telemetry(
    telemetry: TelemetryCreate,
    db: Session = Depends(get_db)
):
    """
    Ingest vehicle telemetry data
    
    - **vehicle_id**: Vehicle identifier
    - **latitude**: Current latitude (-90 to 90)
    - **longitude**: Current longitude (-180 to 180)
    - **speed**: Current speed in km/h
    - **fuel_level**: Fuel level percentage (0-100)
    """
    # Verify vehicle exists
    vehicle = db.query(VehicleModel).filter(
        VehicleModel.vehicle_id == telemetry.vehicle_id
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle {telemetry.vehicle_id} not found. Please register the vehicle first."
        )
    
    # Create telemetry record
    db_telemetry = TelemetryModel(**telemetry.model_dump())
    db.add(db_telemetry)
    
    # Update vehicle's current position
    vehicle.current_lat = telemetry.latitude
    vehicle.current_lon = telemetry.longitude
    vehicle.status = "in_transit" if telemetry.speed > 5 else "idle"
    
    db.commit()
    db.refresh(db_telemetry)
    
    logger.info(f"Telemetry ingested for vehicle {telemetry.vehicle_id}")
    return db_telemetry


@router.post("/batch", status_code=status.HTTP_201_CREATED)
async def ingest_telemetry_batch(
    telemetry_list: List[TelemetryCreate],
    db: Session = Depends(get_db)
):
    """
    Ingest multiple telemetry records at once
    
    Useful for bulk data ingestion from multiple vehicles
    """
    created_records = []
    
    for telemetry in telemetry_list:
        # Verify vehicle exists
        vehicle = db.query(VehicleModel).filter(
            VehicleModel.vehicle_id == telemetry.vehicle_id
        ).first()
        
        if vehicle:
            db_telemetry = TelemetryModel(**telemetry.model_dump())
            db.add(db_telemetry)
            created_records.append(telemetry.vehicle_id)
            
            # Update vehicle position
            vehicle.current_lat = telemetry.latitude
            vehicle.current_lon = telemetry.longitude
    
    db.commit()
    
    logger.info(f"Batch telemetry ingested for {len(created_records)} vehicles")
    return {
        "message": "Batch telemetry ingested successfully",
        "records_created": len(created_records),
        "vehicle_ids": created_records
    }


@router.get("/", response_model=List[Telemetry])
async def get_all_telemetry(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve all telemetry records
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    telemetry = db.query(TelemetryModel).order_by(
        TelemetryModel.timestamp.desc()
    ).offset(skip).limit(limit).all()
    
    return telemetry


@router.get("/vehicle/{vehicle_id}", response_model=List[Telemetry])
async def get_vehicle_telemetry(
    vehicle_id: str,
    skip: int = 0,
    limit: int = 100,
    hours: Optional[int] = Query(None, description="Get telemetry from last N hours"),
    db: Session = Depends(get_db)
):
    """
    Get telemetry data for a specific vehicle
    
    - **vehicle_id**: Vehicle identifier
    - **skip**: Pagination offset
    - **limit**: Maximum records to return
    - **hours**: Optional - get only records from last N hours
    """
    # Verify vehicle exists
    vehicle = db.query(VehicleModel).filter(
        VehicleModel.vehicle_id == vehicle_id
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle {vehicle_id} not found"
        )
    
    query = db.query(TelemetryModel).filter(
        TelemetryModel.vehicle_id == vehicle_id
    )
    
    # Filter by time if specified
    if hours:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(TelemetryModel.timestamp >= cutoff_time)
    
    telemetry = query.order_by(
        TelemetryModel.timestamp.desc()
    ).offset(skip).limit(limit).all()
    
    if not telemetry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No telemetry found for vehicle {vehicle_id}"
        )
    
    return telemetry


@router.get("/vehicle/{vehicle_id}/latest")
async def get_latest_telemetry(
    vehicle_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the most recent telemetry record for a vehicle
    
    - **vehicle_id**: Vehicle identifier
    """
    telemetry = db.query(TelemetryModel).filter(
        TelemetryModel.vehicle_id == vehicle_id
    ).order_by(TelemetryModel.timestamp.desc()).first()
    
    if not telemetry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No telemetry found for vehicle {vehicle_id}"
        )
    
    return telemetry


@router.get("/vehicle/{vehicle_id}/trajectory")
async def get_vehicle_trajectory(
    vehicle_id: str,
    hours: int = Query(24, description="Time window in hours"),
    db: Session = Depends(get_db)
):
    """
    Get vehicle trajectory (path of movement) over time
    
    Returns coordinates and timestamps for visualizing on a map
    
    - **vehicle_id**: Vehicle identifier
    - **hours**: Time window to fetch (default 24 hours)
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    telemetry = db.query(TelemetryModel).filter(
        TelemetryModel.vehicle_id == vehicle_id,
        TelemetryModel.timestamp >= cutoff_time
    ).order_by(TelemetryModel.timestamp.asc()).all()
    
    if not telemetry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No trajectory data found for vehicle {vehicle_id}"
        )
    
    trajectory = [
        {
            "latitude": t.latitude,
            "longitude": t.longitude,
            "timestamp": t.timestamp.isoformat(),
            "speed": t.speed
        }
        for t in telemetry
    ]
    
    return {
        "vehicle_id": vehicle_id,
        "trajectory": trajectory,
        "total_points": len(trajectory),
        "time_range": {
            "start": telemetry[0].timestamp.isoformat(),
            "end": telemetry[-1].timestamp.isoformat()
        }
    }


@router.delete("/vehicle/{vehicle_id}")
async def delete_vehicle_telemetry(
    vehicle_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete all telemetry data for a specific vehicle
    
    - **vehicle_id**: Vehicle identifier
    """
    deleted_count = db.query(TelemetryModel).filter(
        TelemetryModel.vehicle_id == vehicle_id
    ).delete()
    
    db.commit()
    
    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No telemetry found for vehicle {vehicle_id}"
        )
    
    logger.info(f"Deleted {deleted_count} telemetry records for vehicle {vehicle_id}")
    return {
        "message": f"Deleted {deleted_count} telemetry records",
        "vehicle_id": vehicle_id
    }
