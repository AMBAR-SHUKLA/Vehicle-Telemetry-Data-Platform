"""
Vehicle Management API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from database.models import Vehicle as VehicleModel, get_db
from api.schemas import Vehicle, VehicleCreate, VehicleUpdate

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/vehicles",
    tags=["vehicles"],
    responses={404: {"description": "Vehicle not found"}}
)


@router.post("/", response_model=Vehicle, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    vehicle: VehicleCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new vehicle in the fleet
    
    - **vehicle_id**: Unique identifier for the vehicle
    - **vehicle_type**: Type of vehicle (truck, van, car)
    - **capacity**: Maximum carrying capacity in kg
    - **current_lat**: Current latitude position
    - **current_lon**: Current longitude position
    """
    # Check if vehicle already exists
    existing_vehicle = db.query(VehicleModel).filter(
        VehicleModel.vehicle_id == vehicle.vehicle_id
    ).first()
    
    if existing_vehicle:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vehicle with ID {vehicle.vehicle_id} already exists"
        )
    
    # Create new vehicle
    db_vehicle = VehicleModel(**vehicle.model_dump())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    
    logger.info(f"Vehicle {vehicle.vehicle_id} registered successfully")
    return db_vehicle


@router.get("/", response_model=List[Vehicle])
async def get_all_vehicles(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve all vehicles in the fleet
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **status**: Filter by vehicle status (optional)
    """
    query = db.query(VehicleModel)
    
    if status:
        query = query.filter(VehicleModel.status == status)
    
    vehicles = query.offset(skip).limit(limit).all()
    return vehicles


@router.get("/{vehicle_id}", response_model=Vehicle)
async def get_vehicle(
    vehicle_id: str,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific vehicle
    
    - **vehicle_id**: Unique vehicle identifier
    """
    vehicle = db.query(VehicleModel).filter(
        VehicleModel.vehicle_id == vehicle_id
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle {vehicle_id} not found"
        )
    
    return vehicle


@router.put("/{vehicle_id}", response_model=Vehicle)
async def update_vehicle(
    vehicle_id: str,
    vehicle_update: VehicleUpdate,
    db: Session = Depends(get_db)
):
    """
    Update vehicle information
    
    - **vehicle_id**: Vehicle to update
    - Updates only provided fields
    """
    db_vehicle = db.query(VehicleModel).filter(
        VehicleModel.vehicle_id == vehicle_id
    ).first()
    
    if not db_vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle {vehicle_id} not found"
        )
    
    # Update only provided fields
    update_data = vehicle_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_vehicle, key, value)
    
    db.commit()
    db.refresh(db_vehicle)
    
    logger.info(f"Vehicle {vehicle_id} updated successfully")
    return db_vehicle


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
    vehicle_id: str,
    db: Session = Depends(get_db)
):
    """
    Remove a vehicle from the fleet
    
    - **vehicle_id**: Vehicle to delete
    - Also deletes all associated telemetry and routes
    """
    vehicle = db.query(VehicleModel).filter(
        VehicleModel.vehicle_id == vehicle_id
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle {vehicle_id} not found"
        )
    
    db.delete(vehicle)
    db.commit()
    
    logger.info(f"Vehicle {vehicle_id} deleted successfully")
    return None


@router.get("/{vehicle_id}/stats")
async def get_vehicle_stats(
    vehicle_id: str,
    db: Session = Depends(get_db)
):
    """
    Get statistics for a specific vehicle
    
    Returns:
    - Total telemetry records
    - Total routes
    - Average speed
    - Average fuel level
    """
    from database.models import Telemetry as TelemetryModel, Route as RouteModel
    from sqlalchemy import func
    
    vehicle = db.query(VehicleModel).filter(
        VehicleModel.vehicle_id == vehicle_id
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle {vehicle_id} not found"
        )
    
    # Calculate statistics
    telemetry_count = db.query(func.count(TelemetryModel.id)).filter(
        TelemetryModel.vehicle_id == vehicle_id
    ).scalar()
    
    avg_speed = db.query(func.avg(TelemetryModel.speed)).filter(
        TelemetryModel.vehicle_id == vehicle_id
    ).scalar()
    
    avg_fuel = db.query(func.avg(TelemetryModel.fuel_level)).filter(
        TelemetryModel.vehicle_id == vehicle_id
    ).scalar()
    
    route_count = db.query(func.count(RouteModel.route_id)).filter(
        RouteModel.vehicle_id == vehicle_id
    ).scalar()
    
    return {
        "vehicle_id": vehicle_id,
        "telemetry_records": telemetry_count or 0,
        "total_routes": route_count or 0,
        "avg_speed_kmh": round(avg_speed, 2) if avg_speed else 0,
        "avg_fuel_level": round(avg_fuel, 2) if avg_fuel else 0,
        "current_status": vehicle.status
    }
