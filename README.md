# Audience Engagement Analyzer

Backend + (optional) frontend that ingest recorded lectures, track audience emotions/attention and generate actionable feedback for speakers.

## Repository layout

```
backend/   FastAPI service, async PostgreSQL persistence, ONNX emotion model  
frontend/  
```

The machine-learning artifacts that are required at runtime live under `backend/app/ml_models/`. All bulky training data, cached IDE settings, and virtual environments were stripped from the repository for a lean release footprint.

## Quick start (backend)

```bash
cd backend
cp .exampleenv .env 
docker compose up --build
```

Services exposed:

| Service  | URL                    | Notes                         |
|----------|------------------------|-------------------------------|
| Backend  | http://localhost:8000  | FastAPI + automatic OpenAPI   |
| Docs     | http://localhost:8000/docs | Interactive Swagger UI |

Metrics JSON files are written under `backend/data/metrics` inside the container (ignored in git). Each entry includes:

- frame-by-frame attention/engagement ratios
- top engagement peaks and dips (with window timestamps)
- automatically generated coaching suggestions