# syntax=docker/dockerfile:1

# ---- Frontend: build the static export ----
FROM node:22-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---- Backend: install deps, then serve the API + static frontend ----
FROM python:3.13-slim AS backend
WORKDIR /app/backend

RUN pip install --no-cache-dir uv

# Install dependencies first so this layer is cached across app-code changes.
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY backend/app ./app
RUN uv sync --locked --no-dev

COPY --from=frontend-build /app/frontend/out /app/frontend/out

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
