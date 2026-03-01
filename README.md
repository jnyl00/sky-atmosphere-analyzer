# Sky Atmosphere Analyzer

A full-stack application that analyzes sky images to detect atmospheric phenomena using YOLO-based computer vision. The frontend is React + Vite + TypeScript with Tailwind CSS. The backend is Python FastAPI with Ultralytics YOLO.

## Features

- **Image Upload**: Drag-and-drop or select images for analysis
- **Real-time Analysis**: YOLO-based classification with fast inference
- **Fallback Strategy**: 4-level fallback system ensures always returns a result
- **History**: Paginated results history with fallback method indicators

## Taxonomy

All predictions map to these labels:
- `clear_sky`
- `clouds`
- `sunset_sunrise`
- `night_sky_stars`
- `fog_mist_haze`
- `rainbow_lightning`

---

## Quick Start

### Prerequisites

- Node.js 18+ and npm (for frontend)
- Python 3.11+ (for backend)
- Docker & Docker Compose (for containerized deployment)

### Local Development

#### Backend

```bash
cd server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .

# Run development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

#### Frontend

```bash
cd client

# Install dependencies
npm install

# Run development server
npm run dev
```

The UI will be available at `http://localhost:5173`

---

## Configuration

### Environment Variables

#### Backend (.env)

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_FILE_SIZE_MB` | 5 | Maximum upload file size |
| `ALLOWED_MIME_TYPES` | image/jpeg,image/png | Allowed file types |
| `CONFIDENCE_THRESHOLD` | 0.1 | Min confidence for predictions |
| `DEFAULT_MODEL` | yolov8n-cls | YOLO model to use |
| `LOG_LEVEL` | INFO | Logging level |
| `CORS_ORIGINS` | * | CORS allowed origins |

#### Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_BACKEND_URL` | http://localhost:8000 | Backend API URL |

---

## API Endpoints

### POST /api/v1/analyze

Upload an image for atmospheric analysis.

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -F "file=@sky.jpg"
```

Response:
```json
{
  "id": "uuid-string",
  "timestamp": "2024-01-01T12:00:00Z",
  "original_filename": "sky.jpg",
  "group": "atmosphere",
  "predictions": [
    {"label": "clouds", "confidence": 0.87},
    {"label": "clear_sky", "confidence": 0.45}
  ],
  "processing_time_ms": 142,
  "fallback_method": null
}
```

### GET /api/v1/results

Get paginated analysis history.

```bash
curl "http://localhost:8000/api/v1/results?page=1&page_size=20"
```

### GET /health

Health check endpoint.

```bash
curl http://localhost:8000/health
```

---

## Production Deployment

### Docker Compose

The easiest way to run the full stack:

```bash
docker-compose up --build
```

- Frontend: http://localhost:80
- Backend API: http://localhost:8000

### Manual Production Build

#### Backend

```bash
cd server
docker build -f server/Dockerfile -t sky-analyzer-server .
docker run -p 8000:8000 sky-analyzer-server
```

#### Frontend

```bash
cd client
npm install
npm run build
# Serve dist/ with nginx or any static file server
```

---

## Testing

### Backend Tests

```bash
cd server
source venv/bin/activate
pip install pytest pytest-asyncio
pytest tests/ -v
```

33 tests covering:
- Taxonomy mapping and fallback strategy
- Storage service
- Validation utilities
