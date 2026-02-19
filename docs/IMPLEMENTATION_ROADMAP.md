# Implementation Roadmap - Week by Week Guide

## 🎯 Phase 1: Foundation Setup (Week 1-2)

### Week 1: Project Setup & Basic API

#### Day 1-2: Environment Setup
```bash
# Create project directory
mkdir vehicle-telemetry-platform
cd vehicle-telemetry-platform

# Initialize git
git init
echo "*.pyc\n__pycache__\n.env\nvenv/\n*.db" > .gitignore

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install basic dependencies
pip install fastapi uvicorn sqlalchemy pydantic python-dotenv
pip freeze > requirements.txt

# Create project structure
mkdir -p api/routers api/models api/schemas
mkdir -p database tests docs
touch api/__init__.py api/main.py
```

#### Day 3-4: First FastAPI Endpoint
**Goal**: Create a simple health check endpoint

**File**: `api/main.py`
```python
from fastapi import FastAPI
from datetime import datetime

app = FastAPI(
    title="Vehicle Telemetry Platform",
    description="Fleet routing optimization system",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "message": "Vehicle Telemetry Platform API",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",  # We'll implement this later
        "engine": "ready"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Run it**:
```bash
python api/main.py
# Visit http://localhost:8000/docs for automatic API documentation
```

#### Day 5-7: Database Models
**Goal**: Set up SQLite database with basic models

**File**: `database/models.py`
```python
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    vehicle_id = Column(String, primary_key=True)
    vehicle_type = Column(String)  # "truck", "van", "car"
    capacity = Column(Float)  # Max weight capacity in kg
    current_lat = Column(Float)
    current_lon = Column(Float)
    status = Column(String, default="idle")  # "idle", "in_transit", "maintenance"
    
    # Relationship
    telemetry_records = relationship("Telemetry", back_populates="vehicle")
    routes = relationship("Route", back_populates="vehicle")

class Telemetry(Base):
    __tablename__ = "telemetry"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(String, ForeignKey("vehicles.vehicle_id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    latitude = Column(Float)
    longitude = Column(Float)
    speed = Column(Float)  # km/h
    fuel_level = Column(Float)  # percentage
    
    vehicle = relationship("Vehicle", back_populates="telemetry_records")

class Route(Base):
    __tablename__ = "routes"
    
    route_id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(String, ForeignKey("vehicles.vehicle_id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    total_distance = Column(Float)  # km
    estimated_time = Column(Float)  # minutes
    status = Column(String, default="planned")  # "planned", "active", "completed"
    
    vehicle = relationship("Vehicle", back_populates="routes")

# Database connection
DATABASE_URL = "sqlite:///./telemetry.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
```

**File**: `api/schemas.py`
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class VehicleBase(BaseModel):
    vehicle_id: str
    vehicle_type: str
    capacity: float
    current_lat: float
    current_lon: float

class VehicleCreate(VehicleBase):
    pass

class Vehicle(VehicleBase):
    status: str
    
    class Config:
        from_attributes = True

class TelemetryBase(BaseModel):
    vehicle_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    speed: float = Field(..., ge=0)
    fuel_level: float = Field(..., ge=0, le=100)

class TelemetryCreate(TelemetryBase):
    pass

class Telemetry(TelemetryBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True
```

**Test the database**:
```bash
python database/models.py  # Creates telemetry.db
```

---

## 🎯 Phase 2: Core Backend (Week 3-4)

### Week 3: Telemetry API Endpoints

**File**: `api/routers/telemetry.py`
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import sys
sys.path.append('..')

from database.models import Telemetry as TelemetryModel, SessionLocal
from api.schemas import Telemetry, TelemetryCreate

router = APIRouter(prefix="/api/v1/telemetry", tags=["telemetry"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=Telemetry)
async def create_telemetry(telemetry: TelemetryCreate, db: Session = Depends(get_db)):
    """
    Ingest vehicle telemetry data
    """
    db_telemetry = TelemetryModel(**telemetry.dict())
    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)
    return db_telemetry

@router.get("/", response_model=List[Telemetry])
async def get_all_telemetry(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all telemetry records
    """
    telemetry = db.query(TelemetryModel).offset(skip).limit(limit).all()
    return telemetry

@router.get("/vehicle/{vehicle_id}", response_model=List[Telemetry])
async def get_vehicle_telemetry(vehicle_id: str, db: Session = Depends(get_db)):
    """
    Get telemetry for a specific vehicle
    """
    telemetry = db.query(TelemetryModel).filter(
        TelemetryModel.vehicle_id == vehicle_id
    ).all()
    
    if not telemetry:
        raise HTTPException(status_code=404, detail="No telemetry found for this vehicle")
    
    return telemetry
```

**File**: `api/routers/vehicles.py`
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import sys
sys.path.append('..')

from database.models import Vehicle as VehicleModel, SessionLocal
from api.schemas import Vehicle, VehicleCreate

router = APIRouter(prefix="/api/v1/vehicles", tags=["vehicles"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=Vehicle)
async def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    """
    Register a new vehicle in the fleet
    """
    # Check if vehicle already exists
    existing = db.query(VehicleModel).filter(
        VehicleModel.vehicle_id == vehicle.vehicle_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Vehicle already registered")
    
    db_vehicle = VehicleModel(**vehicle.dict())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

@router.get("/", response_model=List[Vehicle])
async def get_all_vehicles(db: Session = Depends(get_db)):
    """
    Get all vehicles in the fleet
    """
    vehicles = db.query(VehicleModel).all()
    return vehicles

@router.get("/{vehicle_id}", response_model=Vehicle)
async def get_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    """
    Get details of a specific vehicle
    """
    vehicle = db.query(VehicleModel).filter(
        VehicleModel.vehicle_id == vehicle_id
    ).first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    return vehicle

@router.put("/{vehicle_id}", response_model=Vehicle)
async def update_vehicle(vehicle_id: str, vehicle: VehicleCreate, db: Session = Depends(get_db)):
    """
    Update vehicle information
    """
    db_vehicle = db.query(VehicleModel).filter(
        VehicleModel.vehicle_id == vehicle_id
    ).first()
    
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    for key, value in vehicle.dict().items():
        setattr(db_vehicle, key, value)
    
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle
```

**Update**: `api/main.py`
```python
from fastapi import FastAPI
from api.routers import telemetry, vehicles
from database.models import init_db

app = FastAPI(
    title="Vehicle Telemetry Platform",
    description="Fleet routing optimization system",
    version="1.0.0"
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Include routers
app.include_router(telemetry.router)
app.include_router(vehicles.router)

@app.get("/")
async def root():
    return {"message": "Vehicle Telemetry Platform API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Week 4: Testing & Validation

**File**: `tests/test_api.py`
```python
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_create_vehicle():
    vehicle_data = {
        "vehicle_id": "V001",
        "vehicle_type": "truck",
        "capacity": 1000.0,
        "current_lat": 37.7749,
        "current_lon": -122.4194
    }
    response = client.post("/api/v1/vehicles/", json=vehicle_data)
    assert response.status_code == 200
    assert response.json()["vehicle_id"] == "V001"

def test_create_telemetry():
    telemetry_data = {
        "vehicle_id": "V001",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "speed": 45.5,
        "fuel_level": 75.0
    }
    response = client.post("/api/v1/telemetry/", json=telemetry_data)
    assert response.status_code == 200
    assert response.json()["vehicle_id"] == "V001"
```

**Run tests**:
```bash
pip install pytest
pytest tests/
```

---

## 🎯 Phase 3: Graph Algorithms (Week 5-7)

### Week 5: Python Graph Implementation (Learning Phase)

**File**: `engine/python/graph.py`
```python
from collections import defaultdict, deque
import heapq
from typing import List, Tuple, Dict

class Graph:
    def __init__(self, vertices: int):
        self.V = vertices
        self.adj = defaultdict(list)  # Adjacency list
        self.weights = {}  # Edge weights
    
    def add_edge(self, u: int, v: int, weight: float):
        """Add weighted edge to graph"""
        self.adj[u].append(v)
        self.weights[(u, v)] = weight
    
    def dijkstra(self, source: int) -> Dict[int, float]:
        """
        Shortest path from source to all vertices
        Returns: Dictionary of distances
        """
        dist = {i: float('inf') for i in range(self.V)}
        dist[source] = 0
        
        pq = [(0, source)]  # (distance, vertex)
        
        while pq:
            d, u = heapq.heappop(pq)
            
            if d > dist[u]:
                continue
            
            for v in self.adj[u]:
                weight = self.weights.get((u, v), 1)
                if dist[u] + weight < dist[v]:
                    dist[v] = dist[u] + weight
                    heapq.heappush(pq, (dist[v], v))
        
        return dist
    
    def get_shortest_path(self, source: int, target: int) -> Tuple[List[int], float]:
        """
        Get shortest path between two nodes
        Returns: (path, distance)
        """
        dist = {i: float('inf') for i in range(self.V)}
        parent = {i: None for i in range(self.V)}
        dist[source] = 0
        
        pq = [(0, source)]
        
        while pq:
            d, u = heapq.heappop(pq)
            
            if u == target:
                break
            
            if d > dist[u]:
                continue
            
            for v in self.adj[u]:
                weight = self.weights.get((u, v), 1)
                if dist[u] + weight < dist[v]:
                    dist[v] = dist[u] + weight
                    parent[v] = u
                    heapq.heappush(pq, (dist[v], v))
        
        # Reconstruct path
        path = []
        current = target
        while current is not None:
            path.append(current)
            current = parent[current]
        path.reverse()
        
        return path, dist[target]

# Example usage
if __name__ == "__main__":
    # Create a simple graph
    g = Graph(5)
    
    # Add edges (representing roads between locations)
    g.add_edge(0, 1, 10.0)  # Location 0 to 1: 10km
    g.add_edge(0, 2, 5.0)
    g.add_edge(1, 3, 1.0)
    g.add_edge(2, 1, 3.0)
    g.add_edge(2, 3, 9.0)
    g.add_edge(3, 4, 2.0)
    
    # Find shortest distances from node 0
    distances = g.dijkstra(0)
    print("Shortest distances from node 0:")
    for node, dist in distances.items():
        print(f"  To node {node}: {dist} km")
    
    # Find shortest path between two nodes
    path, distance = g.get_shortest_path(0, 4)
    print(f"\nShortest path from 0 to 4: {path}")
    print(f"Total distance: {distance} km")
```

**Test it**:
```bash
python engine/python/graph.py
```

---

## 🎯 Key Milestones Checklist

### Phase 1 ✓
- [ ] FastAPI server running
- [ ] Database created with tables
- [ ] Basic health check endpoint
- [ ] API documentation at /docs

### Phase 2 ✓
- [ ] Vehicle registration working
- [ ] Telemetry ingestion working
- [ ] Data validation in place
- [ ] Unit tests passing

### Phase 3 (In Progress)
- [ ] Graph class implemented
- [ ] Dijkstra's algorithm working
- [ ] Shortest path calculation
- [ ] Ready for C++ implementation

---

## 📊 Testing Your Progress

After each week, test with these commands:

```bash
# Week 1-2: Check API
curl http://localhost:8000/
curl http://localhost:8000/health

# Week 3-4: Test endpoints
curl -X POST http://localhost:8000/api/v1/vehicles/ \
  -H "Content-Type: application/json" \
  -d '{"vehicle_id":"V001","vehicle_type":"truck","capacity":1000,"current_lat":37.7749,"current_lon":-122.4194}'

curl -X POST http://localhost:8000/api/v1/telemetry/ \
  -H "Content-Type: application/json" \
  -d '{"vehicle_id":"V001","latitude":37.7749,"longitude":-122.4194,"speed":45.5,"fuel_level":75.0}'

# Week 5: Test graph algorithms
python engine/python/graph.py
```

---

## 🚀 Next Steps

Continue with:
1. Week 6-7: Advanced graph algorithms (Push-Relabel, Gomory-Hu)
2. Week 8-9: C++ implementation and parallelization
3. Week 10-11: Docker and CI/CD
4. Week 12: Final testing and documentation

Each phase builds on the previous one, so make sure you complete and test each section before moving forward!
