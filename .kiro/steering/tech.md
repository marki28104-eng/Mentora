# Technology Stack

## Frontend
- **Framework**: React 18
- **UI Library**: Mantine UI components
- **State Management**: React Query
- **Routing**: React Router
- **HTTP Client**: Axios
- **Icons**: Tabler Icons React

## Backend
- **Framework**: FastAPI
- **Runtime**: Python 3.9+
- **ASGI Server**: Uvicorn
- **Database ORM**: SQLAlchemy with Alembic migrations
- **Database**: MySQL (with asyncpg driver)
- **Caching**: Redis
- **Background Jobs**: Celery
- **Authentication**: JWT with python-jose
- **Password Hashing**: Passlib with bcrypt
- **File Storage**: AWS S3 (boto3)
- **AI Integration**: Google Cloud AI Platform, Google Generative AI
- **Testing**: pytest with pytest-asyncio

## Development Tools
- **Package Management**: npm (frontend), pip (backend)
- **Process Management**: concurrently for running multiple services
- **Environment**: python-dotenv for configuration

## Common Commands

### Setup
```bash
# Install all dependencies
npm run setup

# Install frontend only
npm run install:frontend

# Install backend only  
npm run install:backend
```

### Development
```bash
# Start both frontend and backend
npm run dev

# Start frontend only (http://localhost:3000)
npm run dev:frontend

# Start backend only (http://localhost:8000)
npm run dev:backend
```

### Testing
```bash
# Run all tests
npm run test

# Frontend tests only
npm run test:frontend

# Backend tests only
npm run test:backend
```

### Build
```bash
# Build frontend for production
npm run build
```

## Environment Configuration

### Prerequisites
- Node.js v16+
- Python 3.9+
- MySQL database
- Redis server
- Google Cloud project with AI Platform enabled
- AWS account for S3 storage

### Environment Files
- Frontend: `frontend/.env` (API URL configuration)
- Backend: `backend/.env` (database, Redis, Google Cloud, AWS, JWT settings)