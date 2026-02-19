"""
Database Models using SQLAlchemy
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()


class Vehicle(Base):
    """Vehicle model - represents a single vehicle in the fleet"""
    __tablename__ = "vehicles"
    
    vehicle_id = Column(String, primary_key=True, index=True)
    vehicle_type = Column(String, nullable=False)  # "truck", "van", "car"
    capacity = Column(Float, nullable=False)  # Maximum weight capacity in kg
    current_lat = Column(Float)
    current_lon = Column(Float)
    status = Column(String, default="idle")  # "idle", "in_transit", "maintenance"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    telemetry_records = relationship("Telemetry", back_populates="vehicle", cascade="all, delete-orphan")
    routes = relationship("Route", back_populates="vehicle", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Vehicle(id={self.vehicle_id}, type={self.vehicle_type}, status={self.status})>"


class Telemetry(Base):
    """Telemetry model - stores real-time vehicle data"""
    __tablename__ = "telemetry"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(String, ForeignKey("vehicles.vehicle_id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed = Column(Float)  # km/h
    fuel_level = Column(Float)  # percentage (0-100)
    
    # Relationship
    vehicle = relationship("Vehicle", back_populates="telemetry_records")
    
    def __repr__(self):
        return f"<Telemetry(vehicle={self.vehicle_id}, time={self.timestamp})>"


class Route(Base):
    """Route model - stores planned and completed routes"""
    __tablename__ = "routes"
    
    route_id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(String, ForeignKey("vehicles.vehicle_id", ondelete="CASCADE"), nullable=False, index=True)
    waypoints = Column(Text)  # JSON string of waypoint coordinates
    total_distance = Column(Float)  # kilometers
    estimated_time = Column(Float)  # minutes
    status = Column(String, default="planned")  # "planned", "active", "completed", "cancelled"
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationship
    vehicle = relationship("Vehicle", back_populates="routes")
    
    def __repr__(self):
        return f"<Route(id={self.route_id}, vehicle={self.vehicle_id}, status={self.status})>"


class OptimizationJob(Base):
    """Stores optimization job requests and results"""
    __tablename__ = "optimization_jobs"
    
    job_id = Column(String, primary_key=True, index=True)
    job_type = Column(String, nullable=False)  # "route_optimization", "capacity_planning", etc.
    parameters = Column(Text)  # JSON string of input parameters
    status = Column(String, default="pending")  # "pending", "running", "completed", "failed"
    result = Column(Text, nullable=True)  # JSON string of results
    execution_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<OptimizationJob(id={self.job_id}, type={self.job_type}, status={self.status})>"


# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./telemetry.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully!")


def get_db():
    """
    Dependency to get database session
    Use in FastAPI routes: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    print("Creating database tables...")
    init_db()
    
    # Test database connection
    print("\nTesting database connection...")
    db = SessionLocal()
    try:
        # Try to query
        result = db.execute("SELECT 1").fetchone()
        print("✓ Database connection successful!")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
    finally:
        db.close()
