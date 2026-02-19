#!/bin/bash

# Vehicle Telemetry Platform - Setup Script
# This script sets up your development environment

echo "🚀 Setting up Vehicle Telemetry Platform..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python version
echo "${BLUE}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"
echo ""

# Create project directory structure
echo "${BLUE}Creating project structure...${NC}"
mkdir -p vehicle-telemetry-platform
cd vehicle-telemetry-platform

# Create all necessary directories
mkdir -p api/routers api/models api/schemas
mkdir -p database
mkdir -p engine/python engine/cpp/src engine/cpp/include
mkdir -p tests/unit tests/integration tests/performance
mkdir -p docker
mkdir -p docs
mkdir -p .github/workflows

# Create __init__.py files
touch api/__init__.py
touch api/routers/__init__.py
touch api/models/__init__.py
touch api/schemas/__init__.py
touch database/__init__.py
touch engine/__init__.py
touch engine/python/__init__.py
touch tests/__init__.py

echo "${GREEN}✓${NC} Directory structure created"
echo ""

# Create virtual environment
echo "${BLUE}Creating virtual environment...${NC}"
python3 -m venv venv
echo "${GREEN}✓${NC} Virtual environment created"
echo ""

# Activate virtual environment
echo "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate
echo "${GREEN}✓${NC} Virtual environment activated"
echo ""

# Create requirements.txt
echo "${BLUE}Creating requirements.txt...${NC}"
cat > requirements.txt << EOF
# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3

# Database
sqlalchemy==2.0.25
alembic==1.13.1

# Testing
pytest==7.4.4
pytest-cov==4.1.0
httpx==0.26.0

# Development
python-dotenv==1.0.0
black==23.12.1
flake8==7.0.0
mypy==1.8.0

# Data processing
numpy==1.26.3
pandas==2.1.4

# For future C++ bindings
pybind11==2.11.1
EOF

echo "${GREEN}✓${NC} requirements.txt created"
echo ""

# Install dependencies
echo "${BLUE}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo "${GREEN}✓${NC} Dependencies installed"
echo ""

# Create .gitignore
echo "${BLUE}Creating .gitignore...${NC}"
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/
dist/
build/

# Database
*.db
*.sqlite
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Docker
*.tar
EOF

echo "${GREEN}✓${NC} .gitignore created"
echo ""

# Create .env file
echo "${BLUE}Creating .env file...${NC}"
cat > .env << EOF
# Database
DATABASE_URL=sqlite:///./telemetry.db

# API
API_HOST=0.0.0.0
API_PORT=8000

# Environment
ENVIRONMENT=development
EOF

echo "${GREEN}✓${NC} .env file created"
echo ""

# Create README
echo "${BLUE}Creating README.md...${NC}"
cat > README.md << EOF
# Vehicle Telemetry Data Platform

A high-performance platform for processing vehicle telemetry data and optimizing fleet routing using advanced graph algorithms and parallel computation.

## Features

- 🚗 Real-time vehicle telemetry ingestion
- 📊 Fleet management and monitoring
- 🗺️ Route optimization using graph algorithms
- ⚡ High-performance parallel computation engine
- 🐳 Dockerized deployment
- 🔄 CI/CD pipeline with GitHub Actions

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy
- **Computation Engine**: C++17, OpenMP, pybind11
- **Database**: PostgreSQL/SQLite
- **Algorithms**: Push-Relabel, Gomory-Hu, Dynamic Programming
- **DevOps**: Docker, GitHub Actions

## Quick Start

### Prerequisites

- Python 3.11+
- C++ compiler (g++ or clang++)
- Docker (optional)

### Installation

1. Clone the repository:
\`\`\`bash
git clone <your-repo-url>
cd vehicle-telemetry-platform
\`\`\`

2. Set up virtual environment:
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

3. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. Initialize database:
\`\`\`bash
python database/models.py
\`\`\`

5. Run the API server:
\`\`\`bash
python api/main.py
\`\`\`

6. Visit http://localhost:8000/docs for API documentation

## Project Structure

\`\`\`
vehicle-telemetry-platform/
├── api/                    # FastAPI application
├── engine/                 # Computation engine (Python & C++)
├── database/              # Database models and migrations
├── tests/                 # Test suite
├── docker/                # Docker configuration
├── docs/                  # Documentation
└── .github/workflows/     # CI/CD pipelines
\`\`\`

## API Endpoints

- \`POST /api/v1/vehicles/\` - Register a new vehicle
- \`GET /api/v1/vehicles/\` - Get all vehicles
- \`POST /api/v1/telemetry/\` - Ingest telemetry data
- \`GET /api/v1/telemetry/vehicle/{id}\` - Get vehicle telemetry
- \`POST /api/v1/optimize/routes\` - Optimize routes
- \`GET /health\` - Health check

## Testing

\`\`\`bash
pytest tests/
\`\`\`

## Documentation

See the \`docs/\` directory for detailed documentation:
- [System Architecture](docs/SYSTEM_ARCHITECTURE.md)
- [Implementation Guide](docs/IMPLEMENTATION_ROADMAP.md)
- [API Reference](http://localhost:8000/docs)

## License

MIT License

## Author

Your Name
EOF

echo "${GREEN}✓${NC} README.md created"
echo ""

# Initialize git repository
echo "${BLUE}Initializing git repository...${NC}"
git init
git add .
git commit -m "Initial project setup"
echo "${GREEN}✓${NC} Git repository initialized"
echo ""

# Print success message
echo ""
echo "${GREEN}========================================${NC}"
echo "${GREEN}✓ Setup complete!${NC}"
echo "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "1. cd vehicle-telemetry-platform"
echo "2. source venv/bin/activate"
echo "3. Follow the IMPLEMENTATION_ROADMAP.md for detailed instructions"
echo ""
echo "To start the API server:"
echo "  python api/main.py"
echo ""
echo "To view API docs, visit:"
echo "  http://localhost:8000/docs"
echo ""
echo "Happy coding! 🚀"
