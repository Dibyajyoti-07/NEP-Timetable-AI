# AI-Based Timetable Generation System

A modern full-stack intelligent timetable generation system with React frontend and FastAPI backend, designed to implement NEP 2020 guidelines for educational institutions.

## Project Structure

```
 backend/                 # FastAPI Backend
    app/                # Application code
    tests/              # Test files
    requirements.txt    # Python dependencies
    .env               # Environment variables
    activate.ps1       # Environment activation
 frontend/               # React TypeScript Frontend
    src/               # Source code
    public/            # Static assets
    package.json       # Node dependencies
    README.md          # Frontend documentation
 start-backend.ps1      # Backend startup script
 start-fullstack.ps1    # Full-stack startup script
 README.md              # This file
```

## Features

### Backend (FastAPI + MongoDB)

- Constraint-based timetable generation using OR-Tools
- Natural language processing with Google Gemini AI
- Support for NEP 2020 multidisciplinary course structures
- Flexible credit-based scheduling
- Support for multiple programs (FYUP, B.Ed, M.Ed, ITEP)
- Handling of teaching practice and field work requirements
- Faculty workload balancing
- Room assignment optimization
- Export to various formats (Excel, PDF, JSON, CSV)
- AI-powered timetable analysis and insights
- Natural language queries for timetable information
- JWT-based authentication
- RESTful API with auto-generated documentation

### Frontend (React + TypeScript)

- Modern Material-UI design system
- Responsive dashboard with real-time updates
- User authentication and session management
- Interactive timetable management interface
- Program and constraint configuration
- AI optimization controls
- Data visualization and analytics
- Multi-format export capabilities

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- MongoDB Atlas account (or local MongoDB 5.0+)

### Quick Start (Recommended)

1. Clone this repository
2. Start both backend and frontend:
   ```powershell
   .\start-fullstack.ps1
   ```
3. Access the applications:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Individual Service Startup

#### Backend Only

````powershell
# Option 1: Use the startup script
.\start-backend.ps1

# Option 2: Direct command (recommended for development)
1. cd backend
2. .\activate.ps1
3.  python -m uvicorn app.main:app
 --reload --host 0.0.0.0 --port 8000

#### Frontend Only

```powershell
cd frontend
npm install
npm run dev
````

### Manual Installation

#### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```
2. Create and activate virtual environment:

   ```bash
   # Windows
   python -m venv venv
   .\activate.ps1

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create `.env` file with your configuration
5. Start the server:

   ```bash
   # Windows PowerShell (Recommended)
   cd "D:\SIH\Copilot Timetable Ai\backend"; & "D:\SIH\Copilot Timetable Ai\backend\venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

   # Or use the activation script and then:
   .\activate.ps1
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start development server:
   ```bash
   npm run dev
   ```

## Technology Stack

### Backend

- **FastAPI** - Modern Python web framework
- **MongoDB/Motor** - NoSQL database with async driver
- **OR-Tools** - Google's constraint solving library
- **Google Gemini** - AI-powered insights and NLP
- **Pydantic** - Data validation and serialization
- **PyJWT** - JSON Web Token authentication
- **Pandas/OpenPyXL** - Data processing and Excel export
- **ReportLab** - PDF generation

### Frontend

- **React 18** - Modern UI library with hooks
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **Material-UI (MUI)** - Professional React components
- **React Query** - Server state management
- **Zustand** - Client state management
- **Axios** - HTTP client with interceptors
- **React Router** - Client-side routing

## API Endpoints

### Authentication

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/users/me` - Get current user

### Timetable Management

- `GET /api/v1/timetables/` - List timetables
- `POST /api/v1/timetables/` - Create timetable
- `POST /api/v1/timetables/{id}/generate` - Generate timetable
- `GET /api/v1/timetables/{id}/export` - Export timetable

### AI Features

- `POST /api/v1/ai/optimize` - AI optimization
- `POST /api/v1/ai/analyze` - Timetable analysis
- `POST /api/v1/ai/query` - Natural language queries

## NEP 2020 Features Implemented

- Multidisciplinary course scheduling
- Credit-based system with flexibility
- Support for project work and community engagement
- Specialized scheduling for teaching education programs
- Multiple entry/exit points support
- Holistic and multidisciplinary education approach

## Development

### Code Structure

- Backend follows clean architecture principles
- Frontend uses component-based architecture
- Shared TypeScript types for API contracts
- Comprehensive error handling and validation

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Deployment

### Using Docker

```bash
# Backend
cd backend
docker build -t timetable-backend .
docker run -p 8000:8000 timetable-backend

# Frontend
cd frontend
docker build -t timetable-frontend .
docker run -p 3000:3000 timetable-frontend
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Check the API documentation at http://localhost:8000/docs
- Review the frontend documentation in `/frontend/README.md`
- Open an issue in the GitHub repository
