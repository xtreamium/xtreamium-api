# Xtreamium Backend

A FastAPI-based backend application for managing Xtream Codes IPTV services with EPG (Electronic Program Guide) support and XMLTV integration.

## Features

- **Xtream Codes API Integration**: Full support for Xtream Codes protocol
- **User Authentication**: JWT-based authentication with FastAPI Users
- **EPG Management**: Electronic Program Guide with XMLTV format support
- **Channel Management**: Stream and channel organization
- **Database Migrations**: Alembic-powered database schema management
- **Background Tasks**: Automated EPG updates and data processing
- **RESTful API**: Clean, documented API with automatic OpenAPI documentation
- **Redis Caching**: High-performance caching layer
- **Docker Support**: Containerized deployment ready

## Tech Stack

- **Framework**: FastAPI 0.111+
- **Database**: SQLAlchemy 2.0+ with SQLite/PostgreSQL support
- **Authentication**: FastAPI Users with JWT
- **Caching**: Redis
- **Migrations**: Alembic
- **Validation**: Pydantic 2.7+
- **ASGI Server**: Uvicorn
- **Python**: 3.12+

## Quick Start

### Prerequisites

- Python 3.12+
- UV package manager (recommended) or pip
- Redis server (for caching)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd xtreamium-backend
   ```

2. **Set up virtual environment** (if not using UV)
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   # Using UV (recommended)
   uv sync

   # Or using pip
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations**
   ```bash
   python scripts/migrate.py upgrade
   ```

6. **Start the application**
   ```bash
   # Development
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

   # Production
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

7. **Access the API documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Configuration

The application uses environment variables for configuration. Key settings include:

```bash
# Database
DATABASE_URL=sqlite:///./app/xtreamium.db

# Server
XTREAMIUM_BACKEND_PORT=8000

# Authentication
SECRET_KEY=your-secret-key-here

# Redis (for caching)
REDIS_URL=redis://localhost:6379

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

## Database Migrations

This project uses Alembic for database migrations:

```bash
# Show current migration status
python scripts/migrate.py current

# Create a new migration
python scripts/migrate.py create "Add new feature"

# Apply migrations
python scripts/migrate.py upgrade

# Show migration history
python scripts/migrate.py history
```

See [docs/MIGRATIONS.md](docs/MIGRATIONS.md) for detailed migration documentation.

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout

### Users
- `GET /api/users/me` - Get current user profile
- `PUT /api/users/me` - Update user profile

### Servers
- `GET /api/servers` - List user's Xtream servers
- `POST /api/servers` - Add new Xtream server
- `PUT /api/servers/{id}` - Update server configuration
- `DELETE /api/servers/{id}` - Remove server

### EPG
- `GET /api/epg` - Get Electronic Program Guide data
- `POST /api/epg/refresh` - Trigger EPG data refresh

### Channels
- `GET /api/channels` - List available channels
- `GET /api/channels/{id}` - Get channel details

## Project Structure

```
xtreamium-backend/
├── app/
│   ├── api/              # API route handlers
│   ├── models/           # SQLAlchemy database models
│   ├── schemas/          # Pydantic schemas for validation
│   ├── services/         # Business logic and services
│   │   ├── data/         # Data access layer
│   │   └── tasks/        # Background tasks
│   └── utils/            # Utility functions and helpers
├── migrations/           # Alembic database migrations
├── scripts/              # Management scripts
├── docs/                 # Documentation
└── tests/               # Test suite
```

## Development

### Running Tests
```bash
pytest
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

### Docker Development
```bash
# Build image
docker build -t xtreamium-backend .

# Run container
docker run -p 8000:8000 xtreamium-backend
```

## Background Tasks

The application includes automated background tasks for:

- **EPG Updates**: Automatic refresh of Electronic Program Guide data
- **Channel Synchronization**: Keeping channel lists up-to-date
- **Data Cleanup**: Removing expired EPG entries

Tasks are automatically registered on application startup.

## Xtream Codes Integration

This backend provides comprehensive support for Xtream Codes APIs:

- Stream authentication and authorization
- Live TV, Movies, and Series management
- EPG data integration with XMLTV format
- Multi-server support for load balancing

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in the `/docs` folder
- Review the API documentation at `/docs` endpoint when running
