# AI Sustainability Consultant

AI Sustainability Consultant is a full-stack application that helps businesses assess their environmental impact, generate sustainability recommendations, and produce polished reports. The platform combines a Next.js frontend with a FastAPI backend and AI-powered agents to streamline carbon analysis and reporting workflows.

## Overview

The product supports:

- User authentication and profile management
- Sustainability assessments and workflow tracking
- AI-driven carbon, financial, planning, recommendation, and critique analysis
- Report generation with export-friendly outputs
- Dashboard views for monitoring reports and progress
- Email notifications and internal orchestration endpoints

## Tech Stack

### Frontend
- Next.js 16
- React 19
- TypeScript
- Tailwind CSS
- Zustand for client state
- Recharts for visualization

### Backend
- FastAPI
- Pydantic and Pydantic Settings
- SQLAlchemy
- Supabase integration
- Resend email delivery
- ReportLab for PDF generation

## Project Structure

```text
backend/
  app/
    agents/          # AI agent implementations
    api/             # FastAPI routers
    middleware/      # Authentication middleware
    models/          # Database models
    orchestrator/    # Workflow orchestration logic
    repositories/    # Data access layer
    schemas/         # Request/response schemas
    services/        # Business logic and integrations
    utils/           # Database/bootstrap helpers

frontend/
  app/              # Next.js app routes and pages
  components/       # Reusable UI components
  services/         # Frontend API clients
  store/            # State stores
```

## Prerequisites

Before running the project locally, make sure you have:

- Python 3.10+ and pip
- Node.js 18+ and npm
- Access to the required environment services:
  - OpenRouter API key
  - Supabase project
  - Resend API key
  - PostgreSQL database

## Environment Variables

Create a .env file in the backend directory with the required variables:

```env
OPENROUTER_API_KEY=your_openrouter_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
DATABASE_URL=your_database_connection_string
JWT_SECRET=your_jwt_secret
RESEND_API_KEY=your_resend_api_key
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

## Running Locally

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- http://localhost:8000
- API docs: http://localhost:8000/api/v1/docs

### 2. Frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 in your browser.

## API Highlights

The backend exposes routes for:

- Authentication: /auth/register, /auth/login, /auth/profile
- Assessments: /assessments
- Workflows: /analysis/{id}/start and /analysis/{id}/status
- Reports: /reports/{id}, /reports/{id}/pdf, /reports/{id}/json
- Emails: /reports/{id}/send-email
- Internal AI orchestration: /internal/...

## Deployment

This repository includes a Render configuration in render.yaml for deploying the backend service. The frontend can be deployed separately on Vercel or another hosting provider.

## Notes

- The backend uses environment validation on startup, so missing environment variables will prevent the app from launching.
- Static report files are stored under the backend static directory.
- The application is designed as a modular AI workflow system, making it easy to extend with additional sustainability agents and integrations.

## License

This project is intended for internal or educational use unless otherwise specified by the repository owner.
