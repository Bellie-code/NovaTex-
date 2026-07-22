# Privacy-Aware Face Recognition Attendance System

## Tech Stack
- Frontend: React + Tailwind + Chart.js
- Backend: FastAPI
- DB: PostgreSQL
- Cache: Redis
- Face AI: InsightFace ArcFace + OpenCV + MediaPipe
- Deployment: Docker Compose

## Running Locally

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
