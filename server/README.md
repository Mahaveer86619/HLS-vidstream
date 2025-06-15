# Server

Backend for HLS VidStream.

## Tech Stack

- **FastAPI** (Python web framework)
- **Docker** (containerization)
- **PostgreSQL** (database)
- **Redis** (caching, message broker)
- **Amazon Web Services (AWS)** (cloud infrastructure)

## Codebase Flow

### Video Upload

- Provides endpoints for generating S3 pre-signed upload URLs.
- Receives video metadata and S3 keys after upload.
- Stores initial video info in PostgreSQL and queues jobs in AWS SQS for processing.
- Worker services transcode videos and update database records with processed video locations.

### Video Retrieval

- Handles video data requests from the frontend.
- Checks Redis cache for video data; falls back to PostgreSQL if needed.
- Returns video metadata and streaming URLs (served via AWS CloudFront).
