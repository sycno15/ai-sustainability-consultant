# AI Sustainability Consultant

An autonomous, multi-agent sustainability consulting platform designed for Small and Medium Enterprises (SMEs). The application ingests operational metrics (energy, fuel, water, waste) and financial parameters, runs a specialized multi-agent workflow to compute emissions and financial ROI, creates a phased implementation roadmap, and generates a downloadable PDF report that is emailed upon approval.

## Project Structure

This is a mono-repo organized as follows:

```text
ai-sustainability-consultant/
├── frontend/             # Next.js 15 App Router Frontend
├── backend/              # FastAPI Backend (REST APIs, Multi-Agent Orchestrator)
├── shared/               # Shared constants, types, or utilities
├── docs/                 # Product and technical specifications
└── seed/                 # Database seed CSV files
```

## Technology Stack

* **Frontend**: Next.js 15 (App Router, TypeScript), Tailwind CSS, shadcn/ui, Zustand, TanStack Query, Recharts, Framer Motion
* **Backend**: FastAPI, SQLAlchemy + Alembic, Pydantic, Uvicorn
* **Database & Services**: Supabase (PostgreSQL, Auth, Private Storage), OpenRouter (LLM integration), Resend (Email automation)

## Quick Start

### Backend Setup

1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Unix/macOS:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment template and fill in your secrets:
   ```bash
   cp .env.example .env
   ```
5. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Run the Next.js development server:
   ```bash
   npm run dev
   ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser.
