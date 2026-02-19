"""
Unit tests for the Vehicle Telemetry API
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app
from database.models import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestRootEndpoints:
    """Test root and health endpoints"""
    
    def test_read_root(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
        assert response.json()["status"] == "running"
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestVehicleEndpoints:
    """Test vehicle management endpoints"""
    
    def test_create_vehicle(self):
        """Test creating a new vehicle"""
        vehicle_data = {
            "vehicle_id": "V001",
            "vehicle_type": "truck",
            "capacity": 1000.0,
            "current_lat": 37.7749,
            "current_lon": -122.4194
        }
        response = client.post("/api/v1/vehicles/", json=vehicle_data)
        assert response.status_code == 201
        assert response.json()["vehicle_id"] == "V001"
        assert response.json()["status"] == "idle"
    
    def test_create_duplicate_vehicle(self):
        """Test creating a vehicle with duplicate ID"""
        vehicle_data = {
            "vehicle_id": "V001",
            "vehicle_type": "truck",
            "capacity": 1000.0,
            "current_lat": 37.7749,
            "current_lon": -122.4194
        }
        # Create first time
        client.post("/api/v1/vehicles/", json=vehicle_data)
        
        # Try to create again
        response = client.post("/api/v1/vehicles/", json=vehicle_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_get_all_vehicles(self):
        """Test retrieving all vehicles"""
        # Create a vehicle first
        vehicle_data = {
            "vehicle_id": "V001",
            "vehicle_type": "truck",
            "capacity": 1000.0,
            "current_lat": 37.7749,
            "current_lon": -122.4194
        }
        client.post("/api/v1/vehicles/", json=vehicle_data)
        
        # Get all vehicles
        response = client.get("/api/v1/vehicles/")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["vehicle_id"] == "V001"
    
    def test_get_vehicle_by_id(self):
        """Test retrieving a specific vehicle"""
        # Create a vehicle
        vehicle_data = {
            "vehicle_id": "V001",
            "vehicle_type": "truck",
            "capacity": 1000.0,
            "current_lat": 37.7749,
            "current_lon": -122.4194
        }
        client.post("/api/v1/vehicles/", json=vehicle_data)
        
        # Get the vehicle
        response = client.get("/api/v1/vehicles/V001")
        assert response.status_code == 200
        assert response.json()["vehicle_id"] == "V001"
    
    def test_get_nonexistent_vehicle(self):
        """Test retrieving a vehicle that doesn't exist"""
        response = client.get("/api/v1/vehicles/VXXX")
        assert response.status_code == 404


class TestTelemetryEndpoints:
    """Test telemetry data endpoints"""
    
    def test_ingest_telemetry(self):
        """Test ingesting telemetry data"""
        # First create a vehicle
        vehicle_data = {
            "vehicle_id": "V001",
            "vehicle_type": "truck",
            "capacity": 1000.0,
            "current_lat": 37.7749,
            "current_lon": -122.4194
        }
        client.post("/api/v1/vehicles/", json=vehicle_data)
        
        # Ingest telemetry
        telemetry_data = {
            "vehicle_id": "V001",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "speed": 45.5,
            "fuel_level": 75.0
        }
        response = client.post("/api/v1/telemetry/", json=telemetry_data)
        assert response.status_code == 201
        assert response.json()["vehicle_id"] == "V001"
        assert response.json()["speed"] == 45.5
    
    def test_ingest_telemetry_invalid_vehicle(self):
        """Test ingesting telemetry for non-existent vehicle"""
        telemetry_data = {
            "vehicle_id": "VXXX",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "speed": 45.5,
            "fuel_level": 75.0
        }
        response = client.post("/api/v1/telemetry/", json=telemetry_data)
        assert response.status_code == 404
    
    def test_get_vehicle_telemetry(self):
        """Test retrieving telemetry for a specific vehicle"""
        # Create vehicle
        vehicle_data = {
            "vehicle_id": "V001",
            "vehicle_type": "truck",
            "capacity": 1000.0,
            "current_lat": 37.7749,
            "current_lon": -122.4194
        }
        client.post("/api/v1/vehicles/", json=vehicle_data)
        
        # Add telemetry
        telemetry_data = {
            "vehicle_id": "V001",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "speed": 45.5,
            "fuel_level": 75.0
        }
        client.post("/api/v1/telemetry/", json=telemetry_data)
        
        # Get telemetry
        response = client.get("/api/v1/telemetry/vehicle/V001")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["vehicle_id"] == "V001"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
