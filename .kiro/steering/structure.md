# Project Structure

## Root Level Organization

```
mentora/
├── frontend/          # React application
├── backend/           # FastAPI application  
├── package.json       # Root package.json with development scripts
├── README.md          # Project documentation
└── .kiro/             # Kiro configuration and specs
```

## Frontend Structure (`frontend/`)

```
frontend/
├── public/
│   └── index.html     # HTML template
├── src/
│   ├── components/    # Reusable React components
│   ├── pages/         # Page-level components
│   ├── services/      # API service functions
│   ├── utils/         # Utility functions
│   ├── App.js         # Main App component
│   └── index.js       # React entry point
├── package.json       # Frontend dependencies
└── .env.example       # Environment template
```

## Backend Structure (`backend/`)

```
backend/
├── app/
│   ├── __init__.py
│   ├── agents/        # AI agent implementations
│   │   └── __init__.py
│   ├── api/           # FastAPI route handlers
│   │   └── __init__.py
│   ├── models/        # SQLAlchemy database models
│   │   └── __init__.py
│   └── services/      # Business logic layer
│       └── __init__.py
├── tests/             # Test files
│   └── __init__.py
├── main.py            # FastAPI application entry point
├── requirements.txt   # Python dependencies
├── pytest.ini        # pytest configuration
├── setup_venv.sh      # Virtual environment setup script
├── .env.example       # Environment template
└── venv/              # Python virtual environment
```

## Architecture Patterns

### Backend Architecture
- **Layered Architecture**: Clear separation between API, services, and models
- **Agent Pattern**: Specialized AI agents for different tasks (planner, explainer, quiz)
- **Service Layer**: Business logic isolated from API routes
- **Repository Pattern**: Data access through SQLAlchemy models

### Frontend Architecture
- **Component-Based**: Reusable components in dedicated folder
- **Page-Based Routing**: Page components for different routes
- **Service Layer**: API calls abstracted into service functions
- **Utility Functions**: Common functionality in utils folder

## File Naming Conventions

### Python (Backend)
- **Files**: snake_case (e.g., `user_service.py`)
- **Classes**: PascalCase (e.g., `UserService`)
- **Functions/Variables**: snake_case (e.g., `get_user_data`)

### JavaScript (Frontend)
- **Components**: PascalCase (e.g., `UserProfile.js`)
- **Files**: camelCase for utilities, PascalCase for components
- **Functions/Variables**: camelCase (e.g., `getUserData`)

## Development Workflow

### Adding New Features
1. **Backend**: Create models → services → API routes → tests
2. **Frontend**: Create components → pages → services → integration
3. **AI Agents**: Implement in `backend/app/agents/` following existing patterns

### Environment Setup
- Copy `.env.example` files to `.env` in both frontend and backend
- Use root-level npm scripts for development workflow
- Backend uses virtual environment in `backend/venv/`

### Testing Structure
- **Backend**: Tests in `backend/tests/` using pytest
- **Frontend**: Tests co-located with components using React Testing Library