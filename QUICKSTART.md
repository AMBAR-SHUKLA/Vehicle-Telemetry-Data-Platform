# 🚀 Quick Start Guide

Get the Vehicle Telemetry Platform running in 5 minutes!

## Prerequisites

- Python 3.11 or higher
- Git

## Installation (Automated)

```bash
# Clone the repository (after you upload to GitHub)
git clone https://github.com/AMBAR-SHUKLA/Vehicle-Telemetry-Data-Platform.git
cd Vehicle-Telemetry-Data-Platform

# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Installation (Manual)

```bash
# Clone and navigate
git clone https://github.com/AMBAR-SHUKLA/Vehicle-Telemetry-Data-Platform.git
cd Vehicle-Telemetry-Data-Platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python database/models.py

# Generate sample data
python scripts/generate_sample_data.py
```

## Run the API Server

```bash
# Start the server
python api/main.py

# Or with uvicorn directly
uvicorn api.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Test the API

### 1. Register a Vehicle

```bash
curl -X POST "http://localhost:8000/api/v1/vehicles/" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "V001",
    "vehicle_type": "truck",
    "capacity": 1000.0,
    "current_lat": 37.7749,
    "current_lon": -122.4194
  }'
```

### 2. Submit Telemetry Data

```bash
curl -X POST "http://localhost:8000/api/v1/telemetry/" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "V001",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "speed": 45.5,
    "fuel_level": 75.0
  }'
```

### 3. Get All Vehicles

```bash
curl http://localhost:8000/api/v1/vehicles/
```

### 4. Get Vehicle Telemetry

```bash
curl http://localhost:8000/api/v1/telemetry/vehicle/V001
```

## Using the Interactive API Docs

1. Go to http://localhost:8000/docs
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Fill in the parameters
5. Click "Execute"
6. See the response below

## Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html  # On Mac
# Or just open htmlcov/index.html in your browser
```

## Test Graph Algorithms

```bash
# Run the graph algorithm examples
python engine/python/graph.py
```

You should see output showing:
- Dijkstra's shortest path calculations
- Path finding between nodes
- Real coordinate-based routing

## Using Docker (Optional)

```bash
# Build and run with Docker Compose
cd docker
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Generate More Sample Data

```bash
# Generate sample vehicles, telemetry, locations, and road networks
python scripts/generate_sample_data.py
```

This creates:
- `sample_vehicles.json` - 10 sample vehicles
- `sample_telemetry.json` - 200 telemetry records
- `sample_locations.json` - 25 delivery locations
- `sample_road_network.json` - 100-node road network
- `api_examples.json` - Sample API requests

## Load Sample Data into API

You can use the generated JSON files to populate your API:

```python
import requests
import json

# Load sample vehicles
with open('sample_vehicles.json', 'r') as f:
    data = json.load(f)
    for vehicle in data['vehicles']:
        requests.post('http://localhost:8000/api/v1/vehicles/', json=vehicle)

# Load sample telemetry
with open('sample_telemetry.json', 'r') as f:
    data = json.load(f)
    for telemetry in data['telemetry']:
        requests.post('http://localhost:8000/api/v1/telemetry/', json=telemetry)
```

## Common Issues & Solutions

### Issue: `ModuleNotFoundError`
**Solution**: Make sure virtual environment is activated and dependencies are installed
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Port 8000 already in use
**Solution**: Kill the process or use a different port
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn api.main:app --port 8001
```

### Issue: Database errors
**Solution**: Reinitialize the database
```bash
rm telemetry.db  # Delete old database
python database/models.py  # Create new one
```

## Project Structure Quick Reference

```
Vehicle-Telemetry-Data-Platform/
├── api/                    # FastAPI application
│   ├── main.py            # Main app (START HERE)
│   ├── routers/           # API endpoints
│   └── schemas.py         # Data validation
├── database/
│   └── models.py          # Database models
├── engine/python/
│   └── graph.py           # Graph algorithms
├── scripts/
│   ├── setup.sh           # Automated setup
│   └── generate_sample_data.py  # Test data
├── tests/
│   └── test_api.py        # API tests
└── docs/                  # Documentation
```

## What to Do Next?

1. **Explore the API**: Try all endpoints in the interactive docs
2. **Read the Documentation**: Check `/docs` folder for detailed guides
3. **Run the Tests**: Make sure everything works
4. **Modify and Experiment**: Change code, see what happens
5. **Follow the Roadmap**: Implement advanced features step by step

## Getting Help

- **Documentation**: See `/docs` folder
- **API Docs**: http://localhost:8000/docs
- **Issues**: Create an issue on GitHub
- **Guides**:
  - System Architecture: `docs/SYSTEM_ARCHITECTURE.md`
  - Implementation Roadmap: `docs/IMPLEMENTATION_ROADMAP.md`
  - Graph Algorithms: `docs/GRAPH_ALGORITHMS_GUIDE.md`

## Development Workflow

```bash
# Make changes to code
# ...

# Run tests
pytest tests/

# Check code style
black .
isort .

# Commit changes
git add .
git commit -m "Description of changes"
git push origin main
```

---

**You're all set! 🎉**

The platform is running and ready for development. Start by exploring the API documentation at http://localhost:8000/docs

For detailed implementation guides, see the `/docs` folder.
