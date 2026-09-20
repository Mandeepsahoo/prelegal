# prelegal
A platform for drafting common legal documents

## Status

🚧 This project is currently in progress and is expected to be completed within 1 week.

## Running the app

Prelegal ships as a single Docker container: FastAPI serves both the API and
the statically-exported Next.js frontend on **http://localhost:8000**.

1. Copy `.env.example` to `.env` and fill in the values.
2. Run the start script for your platform:

   ```bash
   # macOS
   scripts/start-mac.sh

   # Linux
   scripts/start-linux.sh
   ```

   ```powershell
   # Windows
   scripts/start-windows.ps1
   ```
3. Stop it with the matching `stop-*` script.

The SQLite database is recreated from scratch every time the container
starts, so no user data persists across restarts.

### Local development (without Docker)

```bash
# Backend (http://localhost:8000)
cd backend
uv sync --group dev
uv run uvicorn app.main:app --reload

# Frontend (http://localhost:3000)
cd frontend
npm install
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

Run backend tests with `uv run pytest` from `backend/`.
