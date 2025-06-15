# Consumer

Handles video retrieval and streaming logic.

## Codebase Flow

- Receives video requests from the frontend.
- Checks Redis cache for video data.
- If not cached, queries PostgreSQL for video metadata and streaming URLs.
- Returns video metadata and HLS streaming URLs (served via AWS CloudFront CDN).
