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
- The backend saves the initial video information to the PostgreSQL database (hosted on AWS Aurora) and places a message into an AWS SQS (Simple Queue Service) queue. This message signals that a new video is ready for processing.

### Retrieving a Video

- The app requests video data from the backend.
- The backend first checks Redis (hosted on AWS ElastiCache) to see if the requested video's data is already cached.
- The backend returns video metadata and a streaming URL (served via AWS CloudFront CDN).
