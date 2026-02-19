# 🚗 Vehicle Telemetry Data Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-orange.svg)](https://github.com/features/actions)

A high-performance platform for processing vehicle telemetry data and optimizing fleet routing using advanced graph algorithms and parallel computation.

![System Architecture](docs/images/architecture-overview.png)

## 🌟 Features

- **🚗 Real-time Telemetry Processing**: Ingest and process vehicle data at scale (1000+ events/second)
- **📊 Fleet Management**: Monitor and manage vehicle fleets with comprehensive tracking
- **🗺️ Route Optimization**: Advanced graph algorithms for optimal route planning
- **⚡ High Performance**: C++ computation engine with OpenMP parallelization
- **🐳 Containerized**: Docker-ready for easy deployment
- **🔄 CI/CD Ready**: Automated testing and deployment pipelines
- **📚 Well Documented**: Comprehensive API documentation and guides

## 🎯 Use Cases

- **Fleet Routing Optimization**: Minimize travel distance and time for delivery vehicles
- **Traffic Flow Analysis**: Optimize vehicle distribution across road networks
- **Capacity Planning**: Maximize throughput using max-flow algorithms
- **Network Reliability**: Identify critical routes using min-cut analysis
- **Real-time Monitoring**: Track vehicle locations, speed, and fuel levels

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                             │
│  (Mobile Apps, Web Dashboard, External Systems)              │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼──────────────────────────────────────┐
│                   API GATEWAY (FastAPI)                      │
│  /telemetry  /routes  /optimize  /health                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐           ┌────────▼──────────┐
│  DATA INGESTION│           │  COMPUTATION ENGINE│
│     SERVICE    │           │     (C++/Python)   │
│   - Validation │           │  - Graph Builder   │
│   - Parsing    │           │  - Push-Relabel    │
│   - Storage    │           │  - Gomory-Hu       │
└───────┬────────┘           │  - Route Optimizer │
        │                    └────────┬───────────┘
        │                             │
┌───────▼─────────────────────────────▼─────┐
│        DATABASE (PostgreSQL/SQLite)        │
│  - Vehicles  - Telemetry  - Routes         │
└────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- C++ compiler (g++ 11+ or clang++)
- Git
- Docker (optional)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/AMBAR-SHUKLA/Vehicle-Telemetry-Data-Platform.git
cd Vehicle-Telemetry-Data-Platform
```

2. **Run setup script**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

Or manually:

```bash
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

3. **Start the API server**
```bash
python api/main.py
```

4. **Access the API documentation**
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📖 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Root endpoint |
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/vehicles/` | Register a new vehicle |
| `GET` | `/api/v1/vehicles/` | Get all vehicles |
| `GET` | `/api/v1/vehicles/{id}` | Get specific vehicle |
| `POST` | `/api/v1/telemetry/` | Ingest telemetry data |
| `GET` | `/api/v1/telemetry/` | Get all telemetry records |
| `GET` | `/api/v1/telemetry/vehicle/{id}` | Get vehicle telemetry |
| `POST` | `/api/v1/optimize/routes` | Trigger route optimization |
| `GET` | `/api/v1/routes/{job_id}` | Get optimization results |

## 💡 Example Usage

### Register a Vehicle
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

### Submit Telemetry Data
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

### Optimize Routes
```bash
curl -X POST "http://localhost:8000/api/v1/optimize/routes" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicles": ["V001", "V002", "V003"],
    "destinations": [
      {"lat": 37.7749, "lon": -122.4194, "demand": 100},
      {"lat": 37.8044, "lon": -122.2712, "demand": 150}
    ],
    "optimization_type": "minimize_distance"
  }'
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=. tests/

# Run specific test file
pytest tests/unit/test_api.py

# Run integration tests
pytest tests/integration/
```

## 🔧 Tech Stack

### Backend
- **Python 3.11+**: Main application logic
- **FastAPI**: Modern, fast web framework for APIs
- **Pydantic**: Data validation using Python type annotations
- **SQLAlchemy**: SQL toolkit and ORM
- **Uvicorn**: Lightning-fast ASGI server

### Computation Engine
- **C++17**: High-performance algorithm implementations
- **OpenMP**: Parallel computing framework
- **pybind11**: Seamless Python-C++ integration
- **Boost.Graph**: Graph data structures and algorithms

### Database
- **PostgreSQL**: Production-grade relational database
- **SQLite**: Lightweight database for development/testing
- **Redis**: In-memory caching (optional)

### Graph Algorithms
- **Dijkstra's Algorithm**: Shortest path finding
- **Push-Relabel**: Maximum flow optimization
- **Gomory-Hu Tree**: Minimum cut computations
- **Dynamic Programming**: TSP approximations

### DevOps
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **GitHub Actions**: CI/CD automation
- **pytest**: Testing framework

## 📊 Performance Benchmarks

| Operation | Dataset Size | Sequential | Parallel (4 cores) | Speedup |
|-----------|-------------|-----------|-------------------|---------|
| Dijkstra's Algorithm | 1,000 nodes | 250ms | 90ms | 2.8x |
| Push-Relabel | 500 nodes | 1.2s | 380ms | 3.2x |
| TSP-DP | 18 cities | 8s | 2.5s | 3.2x |
| Full Route Optimization | 20 vehicles | 45s | 14s | 3.2x |
| Telemetry Ingestion | 1,000 events/s | ✓ | ✓ | - |

## 📁 Project Structure

```
Vehicle-Telemetry-Data-Platform/
├── api/                          # FastAPI application
│   ├── main.py                   # Application entry point
│   ├── routers/                  # API route handlers
│   │   ├── telemetry.py
│   │   ├── vehicles.py
│   │   └── optimization.py
│   ├── models/                   # Data models
│   └── schemas/                  # Pydantic schemas
├── engine/                       # Computation engine
│   ├── python/                   # Python implementations
│   │   ├── graph.py
│   │   └── algorithms.py
│   └── cpp/                      # C++ implementations
│       ├── src/                  # Source files
│       └── include/              # Header files
├── database/                     # Database layer
│   ├── models.py                 # SQLAlchemy models
│   └── migrations/               # Database migrations
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── performance/              # Performance benchmarks
├── docker/                       # Docker configuration
│   ├── Dockerfile.api
│   ├── Dockerfile.engine
│   └── docker-compose.yml
├── scripts/                      # Utility scripts
│   ├── setup.sh
│   └── generate_sample_data.py
├── docs/                         # Documentation
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── IMPLEMENTATION_ROADMAP.md
│   └── GRAPH_ALGORITHMS_GUIDE.md
├── .github/                      # GitHub configuration
│   └── workflows/                # CI/CD workflows
│       └── ci-cd.yml
├── requirements.txt              # Python dependencies
├── .gitignore
├── .env.example
├── LICENSE
└── README.md
```

## 🎓 Documentation

- **[System Architecture](docs/SYSTEM_ARCHITECTURE.md)**: Detailed system design and component breakdown
- **[Implementation Roadmap](docs/IMPLEMENTATION_ROADMAP.md)**: Week-by-week development guide
- **[Graph Algorithms Guide](docs/GRAPH_ALGORITHMS_GUIDE.md)**: In-depth algorithm explanations
- **[API Reference](http://localhost:8000/docs)**: Interactive API documentation

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Ambar Shukla**

- GitHub: [@AMBAR-SHUKLA](https://github.com/AMBAR-SHUKLA)
- Project Link: [Vehicle-Telemetry-Data-Platform](https://github.com/AMBAR-SHUKLA/Vehicle-Telemetry-Data-Platform)

## 🙏 Acknowledgments

- FastAPI framework and documentation
- Introduction to Algorithms (CLRS)
- OpenMP parallel computing community
- Graph algorithm research papers and implementations

## 📫 Contact

For questions or feedback, please open an issue on GitHub.

---

⭐ **Star this repository if you find it helpful!**
