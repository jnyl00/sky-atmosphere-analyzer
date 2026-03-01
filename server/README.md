# Backend

## Setup

Using pyproject.toml:

```bash
cd server
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e .
```

## Run

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### POST /api/v1/analyze

Analyzes an image and returns atmospheric phenomenon predictions.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (image/jpeg or image/png, max 5MB)

**Response:**
```json
{
  "id": "uuid-string",
  "timestamp": "2026-03-01T12:00:00Z",
  "original_filename": "sky.jpg",
  "group": "atmosphere",
  "predictions": [
    {"label": "clouds", "confidence": 0.87},
    {"label": "sunset_sunrise", "confidence": 0.45}
  ],
  "processing_time_ms": 142
}
```

**Error Responses:**
| Status | Detail |
|--------|--------|
| 413 | "File too large. Maximum size: 5MB" |
| 415 | "Unsupported file type. Allowed: image/jpeg, image/png" |
| 400 | "Invalid or corrupted image file" |

### GET /health

Health check endpoint.

Returns: `{"status": "healthy"}`

### GET /api/v1/results

Returns paginated past upload results from in-memory storage.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | int | 1 | Page number (1-indexed) |
| page_size | int | 20 | Items per page (max 100) |

**Response:**
```json
{
  "results": [
    {
      "id": "uuid-string",
      "timestamp": "2026-03-01T12:00:00Z",
      "original_filename": "sky.jpg",
      "group": "atmosphere",
      "predictions": [
        {"label": "clouds", "confidence": 0.87}
      ],
      "processing_time_ms": 142
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 45,
    "total_pages": 3
  }
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_FILE_SIZE_MB` | 5 | Maximum upload file size |
| `ALLOWED_MIME_TYPES` | image/jpeg,image/png | Allowed file types |
| `CONFIDENCE_THRESHOLD` | 0.1 | Min confidence for predictions |
| `DEFAULT_MODEL` | yolov8n-cls | YOLO model to use |
| `MODEL_CACHE_DIR` | ./models | Model cache directory (see note below) |
| `LOG_LEVEL` | INFO | Logging level |
| `CORS_ORIGINS` | http://localhost:5173 | CORS allowed origins (comma-separated) |
| `UVICORN_TIMEOUT_KEEP_ALIVE` | 5 | Keep-alive timeout in seconds |
| `UVICORN_TIMEOUT_GRACE_PERIOD` | 10 | Grace period for shutdown in seconds |

> **Note on `MODEL_CACHE_DIR`**: In Docker, the model cache directory is fixed to `/app/server/.models` via volume mount. This setting is primarily useful for local development outside Docker.

All settings are managed via **Pydantic** in `app/utils/config.py`. The application uses `pydantic-settings` for type-safe configuration loading from environment variables.

### Pydantic Models

Request/response models are defined using Pydantic in the handlers:

- `AnalyzeRequest` / `AnalyzeResponse` - Image analysis endpoint
- `HistoryResponse` - Paginated results endpoint with `PaginationInfo` model
- `HealthResponse` - Health check response

## Taxonomy & Fallback Strategy

The system maps raw YOLO predictions to 6 required atmospheric labels:

- `clear_sky`
- `clouds`
- `sunset_sunrise`
- `night_sky_stars`
- `fog_mist_haze`
- `rainbow_lightning`

### 4-Level Fallback Strategy

When the YOLO model returns predictions that don't directly match taxonomy labels, the system uses a 4-level fallback:

1. **Primary Mapping** - Direct match between YOLO label and taxonomy label (e.g., "clouds" → "clouds")
2. **Heuristic Keyword Mapping** - Rule-based mapping using keyword matching (e.g., "overcast" → "clouds", "star" → "night_sky_stars")
3. **Brightness Analysis** - Analyze image brightness histogram to classify as day/night (e.g., dark images → "night_sky_stars")
4. **Default Fallback** - Return "clear_sky" as safe fallback if no match found

## Architecture

```
server/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── train.py             # Fine-tuning script (optional)
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── analyze.py       # POST /api/v1/analyze endpoint handler
│   │   └── history.py       # GET /api/v1/results endpoint handler
│   ├── models/
│   │   ├── __init__.py
│   │   ├── yolo_model.py    # YOLO singleton wrapper
│   │   └── taxonomy.py      # Label mapping layer (4-level fallback)
│   ├── services/
│   │   ├── __init__.py
│   │   └── storage.py       # In-memory storage for results
│   └── utils/
│       ├── __init__.py
│       ├── config.py        # Pydantic settings management
│       └── validation.py     # File validation
├── pyproject.toml
├── .env
└── .env.example
```

### Component Responsibilities

| Layer | Component | Responsibility |
|-------|-----------|----------------|
| API | `main.py` | FastAPI app, CORS, lifespan events |
| Handler | `handlers/analyze.py` | Request orchestration, file validation |
| Handler | `handlers/history.py` | Pagination logic, result retrieval |
| Model | `models/yolo_model.py` | Singleton YOLO classifier (loaded once at startup) |
| Model | `models/taxonomy.py` | 4-level fallback strategy for label mapping |
| Storage | `services/storage.py` | In-memory storage for upload results |
| Utils | `utils/config.py` | Pydantic settings management |
| Utils | `utils/validation.py` | File size, MIME type, image corruption checks |

## Testing

The backend uses **pytest** with **pytest-asyncio** for testing.

### Test Framework

- **pytest** - Testing framework
- **pytest-asyncio** - Async test support for FastAPI handlers
- **pytest-cov** - Code coverage reporting

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_taxonomy.py

# Run with verbose output
pytest -v
```

### Test Coverage

Tests are located in the `tests/` folder and cover:

- **Taxonomy** (`tests/test_taxonomy.py`) - Label mapping and 4-level fallback strategy
- **Storage** (`tests/test_storage.py`) - In-memory result storage operations
- **Validation** (`tests/test_validation.py`) - File validation (size, MIME type, corruption)

## Productionization

### Docker

Build the image:

```bash
docker build -t sky-atmosphere-analyzer ./server
```

Run the container:

```bash
docker run -p 8000:8000 --env-file server/.env sky-atmosphere-analyzer
```

### Docker Compose

For the full stack (frontend + backend), run from the project root:

```bash
docker-compose up --build
```

This starts:
- Frontend on `http://localhost:80`
- Backend on `http://localhost:8000`

For production:

```bash
docker-compose -f docker-compose.prod.yml up --build
```

### Gunicorn with Uvicorn Workers

For production, use Gunicorn with Uvicorn workers for better concurrency:

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

Recommended worker count: 2-4 (adjust based on CPU cores and memory).

### GPU Support

To enable GPU inference, ensure CUDA is available and install GPU-enabled PyTorch. The YOLO model will automatically use GPU if available.

### Security Considerations

#### Current
- CORS is configurable via `CORS_ORIGINS` environment variable
- File uploads are validated for type and size
- Temporary files are cleaned up after processing

#### Future
- Authentication
- No rate limiting - consider adding for public deployments

### Scaling Considerations

- **Stateless**: The API is stateless; results are stored in-memory only
- **Session persistence**: Results are lost on server restart (add Redis/database for persistence)
- **Model loading**: Model loads once at startup; subsequent requests share it
- **Memory**: YOLO model consumes ~100-200MB RAM; workers share the model instance

## Limitations

1. **Pretrained model accuracy**: Uses pretrained `yolov8n-cls` which outputs ImageNet classes; keyword mapping provides fallbacks but may not be accurate for sky images
2. **No fine-tuned model**: Training script exists but model not trained; run `python train.py` to create `models/sky_classifier.pt`
3. **In-memory storage**: Results are lost on server restart
4. **Single-node**: No horizontal scaling without external storage
5. **Limited labels**: Only 4 of 6 taxonomy classes have training data (fog_mist_haze, rainbow_lightning have 0 images)

## Next Steps

1. **Fine-tune the model**: Run `python train.py` to create a custom classifier
2. **Add persistence**: Replace in-memory storage with Redis or database
3. **Add authentication**: Implement API keys or OAuth for production
4. **Restrict CORS**: Configure `CORS_ORIGINS` in production
5. **Add rate limiting**: Prevent abuse with slowapi or similar
6. **Add monitoring**: Integrate Prometheus metrics, health checks
