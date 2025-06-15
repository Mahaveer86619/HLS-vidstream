# Client

Frontend for HLS VidStream.

## Tech Stack

- **Flutter** (cross-platform UI toolkit)
- **Bloc** (state management)

## Codebase Flow

### Uploading a Video

- The Flutter app requests a pre-signed S3 upload URL from the FastAPI backend.
- The video file is uploaded directly to S3 using this URL.
- After upload, the app sends video metadata and the S3 key to the backend.
- The backend queues the video for processing and transcoding.

### Retrieving a Video

- The app requests video data from the backend.
- The backend checks Redis for cached data; if not found, it queries PostgreSQL.
- The backend returns video metadata and a streaming URL (served via AWS CloudFront CDN).
