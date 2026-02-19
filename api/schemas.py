"""
Pydantic Schemas for Request/Response Validation
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
import json


# ==================== Vehicle Schemas ====================

class VehicleBase(BaseModel):
    """Base vehicle schema"""
    vehicle_id: str = Field(..., description="Unique vehicle identifier", examples=["V001"])
    vehicle_type: str = Field(..., description="Type of vehicle", examples=["truck", "van", "car"])
    capacity: float = Field(..., gt=0, description="Maximum capacity in kg", examples=[1000.0])
    current_lat: float = Field(..., ge=-90, le=90, description="Current latitude")
    current_lon: float = Field(..., ge=-180, le=180, description="Current longitude")


class VehicleCreate(VehicleBase):
    """Schema for creating a new vehicle"""
    pass


class VehicleUpdate(BaseModel):
    """Schema for updating vehicle information"""
    vehicle_type: Optional[str] = None
    capacity: Optional[float] = Field(None, gt=0)
    current_lat: Optional[float] = Field(None, ge=-90, le=90)
    current_lon: Optional[float] = Field(None, ge=-180, le=180)
    status: Optional[str] = None


class Vehicle(VehicleBase):
    """Complete vehicle schema with database fields"""
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Telemetry Schemas ====================

class TelemetryBase(BaseModel):
    """Base telemetry schema"""
    vehicle_id: str = Field(..., description="Vehicle identifier")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    speed: float = Field(..., ge=0, description="Speed in km/h", examples=[45.5])
    fuel_level: float = Field(..., ge=0, le=100, description="Fuel level percentage", examples=[75.0])


class TelemetryCreate(TelemetryBase):
    """Schema for creating telemetry record"""
    pass


class Telemetry(TelemetryBase):
    """Complete telemetry schema with database fields"""
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


# ==================== Route Schemas ====================

class Waypoint(BaseModel):
    """Single waypoint in a route"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    name: Optional[str] = None
    arrival_time: Optional[str] = None


class RouteBase(BaseModel):
    """Base route schema"""
    vehicle_id: str
    waypoints: List[Waypoint]
    total_distance: Optional[float] = Field(None, ge=0, description="Total distance in km")
    estimated_time: Optional[float] = Field(None, ge=0, description="Estimated time in minutes")


class RouteCreate(RouteBase):
    """Schema for creating a new route"""
    pass


class Route(RouteBase):
    """Complete route schema with database fields"""
    route_id: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
    
    @field_validator('waypoints', mode='before')
    @classmethod
    def parse_waypoints(cls, v):
        """Parse waypoints from JSON string if needed"""
        if isinstance(v, str):
            return json.loads(v)
        return v


# ==================== Optimization Schemas ====================

class DeliveryLocation(BaseModel):
    """Delivery destination"""
    location_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    demand: float = Field(..., gt=0, description="Delivery demand in kg")
    time_window_start: Optional[str] = Field(None, description="Earliest delivery time (HH:MM)")
    time_window_end: Optional[str] = Field(None, description="Latest delivery time (HH:MM)")


class OptimizationRequest(BaseModel):
    """Request for route optimization"""
    vehicles: List[str] = Field(..., description="List of vehicle IDs to optimize")
    destinations: List[DeliveryLocation] = Field(..., description="Delivery locations")
    optimization_type: str = Field(
        default="minimize_distance",
        description="Optimization objective",
        examples=["minimize_distance", "minimize_time", "balance_load"]
    )
    max_computation_time: Optional[int] = Field(
        default=300,
        description="Maximum computation time in seconds"
    )


class OptimizationResult(BaseModel):
    """Result of route optimization"""
    job_id: str
    status: str
    vehicle_routes: Optional[List[Route]] = None
    total_distance: Optional[float] = None
    total_time: Optional[float] = None
    execution_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime


# ==================== Response Schemas ====================

class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    services: dict


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime


class SuccessResponse(BaseModel):
    """Generic success response"""
    message: str
    data: Optional[dict] = None
    timestamp: datetime
