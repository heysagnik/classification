# Satellite Image AI Backend

Production-ready FastAPI backend for strict sequential, async, multi-model satellite image processing.

## Features

- Strict sequential 3-step pipeline (no parallel model calls)
- Async external API calls with shared httpx.AsyncClient instances
- Rate-limit aware retries for Gemini and Groq (429 and transient 5xx)
- Strong file validation for JPG, PNG, TIF/TIFF
- Structured response for UI progress: step1, step2, step3, final
- Logging for request lifecycle and step start/end events

## Pipeline Architecture

The POST /analyze endpoint runs this exact order:

1. Step 1 (Gemini Vision): Analyze uploaded image
2. Step 2 (Groq Llama): Generate sustainability and visual improvements from Step 1 JSON
3. Step 3 (Gemini Image): Reimagine the image using original image + improvements

No batching and no parallel Gemini calls are used.

## Environment Variables

Create or edit backend/.env:

```env
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key

# Optional model overrides
GEMINI_VISION_MODEL=gemini-3-flash-preview
GEMINI_IMAGE_MODEL=gemini-2.5-flash
GROQ_MODEL=llama3-8b-8192

# App settings
CORS_ALLOW_ORIGINS=*
LOG_LEVEL=INFO
```

## Run Locally

From backend directory:

```bash
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```

Docs: http://127.0.0.1:8001/docs

## Endpoints

### GET /health

Response:

```json
{
  "status": "ok",
  "gemini_configured": true,
  "groq_configured": true
}
```

### POST /analyze

Request:

- Content-Type: multipart/form-data
- Field name: file
- Allowed types: jpg, jpeg, png, tif, tiff

Response shape:

```json
{
  "classification": "Urban fringe",
  "features": [
    {
      "name": "Residential blocks",
      "coordinates": [132.0, 88.0, 240.0, 150.0]
    }
  ],
  "description": "Mixed built-up area with sparse vegetation.",
  "improvements": [
    "Add connected tree corridors",
    "Install rainwater harvesting zones"
  ],
  "generated_image": "iVBORw0KGgoAAAANSUhEUgAA...",
  "step1": {
    "classification": "Urban fringe",
    "features": [
      {
        "name": "Residential blocks",
        "coordinates": [132.0, 88.0, 240.0, 150.0]
      }
    ],
    "description": "Mixed built-up area with sparse vegetation."
  },
  "step2": {
    "improvements": [
      "Add connected tree corridors",
      "Install rainwater harvesting zones"
    ]
  },
  "step3": "iVBORw0KGgoAAAANSUhEUgAA...",
  "final": {
    "classification": "Urban fringe",
    "features": [
      {
        "name": "Residential blocks",
        "coordinates": [132.0, 88.0, 240.0, 150.0]
      }
    ],
    "description": "Mixed built-up area with sparse vegetation.",
    "improvements": [
      "Add connected tree corridors",
      "Install rainwater harvesting zones"
    ],
    "generated_image": "iVBORw0KGgoAAAANSUhEUgAA..."
  }
}
```

## Error Handling

| Status | Case |
|--------|------|
| 400 | Missing file, empty upload, unsupported format, invalid image |
| 413 | File exceeds size limit |
| 502 | Gemini or Groq upstream API failure |
| 500 | Unexpected internal error |

## Logging

Logs are written to backend/logs/app.log and include:

- Request received
- Step 1 start/end
- Step 2 start/end
- Step 3 start/end
- Errors with stack traces

## Project Structure

```text
backend/
  main.py
  .env
  requirements.txt
  logs/
    app.log
  services/
    gemini_service.py
    groq_service.py
  schemas/
    response_schema.py
  utils/
    image_utils.py
```

## Quick Test

```bash
curl -X POST \
  -F "file=@sample.jpg" \
  http://127.0.0.1:8001/analyze
```

## Deployment Notes

- Keep API keys only in environment variables
- Use explicit CORS origins in production
- Keep LOG_LEVEL at INFO or WARNING in production
