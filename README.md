# HLS VidStream

A full-stack video streaming application inspired by YouTube, built with modern technologies for scalable and efficient video delivery.

## Features

- Video upload, streaming, and playback (HLS)
- User authentication and profiles
- Comments, likes, and subscriptions
- Responsive UI (Flutter)
- Scalable backend with FastAPI, Docker, and AWS

## Tech Stack

- **Frontend:** Flutter, Bloc
- **Backend:** FastAPI, Docker
- **Database:** PostgreSQL
- **Cache:** Redis
- **Cloud:** Amazon Web Services (AWS)
- **Streaming:** HLS (HTTP Live Streaming)

## Getting Started

### Clone the repository

```bash
git clone https://github.com/yourusername/HLS-vidstream.git
cd HLS-vidstream
```

### Directory Structure

- `client/` - Flutter frontend
- `server/` - FastAPI backend

### Setup

See the `README.md` files in the `client` and `server` directories for tech stack details and further setup instructions.

---

# Codebase

## ⬆️ When Uploading a Video

The upload process is designed to be efficient and non-blocking. It offloads the heavy lifting of video processing to a separate, asynchronous service.

1. **Get Upload URL:** The Flutter frontend application initiates the upload by calling an endpoint on the FastAPI backend (e.g., `/upload/get-url`). All backend requests are routed through an AWS Load Balancer for scalability.
2. **Direct Upload to S3:** The backend generates and returns a secure, temporary S3 pre-signed URL. This allows the Flutter app to upload the raw video file directly to an AWS S3 bucket (`raw_videos`) without needing to handle AWS credentials on the client-side.
3. **Send Metadata:** After the direct upload to S3 is complete, the Flutter app sends the video's metadata (title, description) and the unique S3 key (the video's filename/path in S3) to another endpoint on the FastAPI backend.
4. **Queue for Processing:** The backend saves the initial video information to the PostgreSQL database (hosted on AWS Aurora) and places a message into an AWS SQS (Simple Queue Service) queue. This message signals that a new video is ready for processing.
5. **Asynchronous Transcoding:** A separate backend worker service (managed by AWS ECS - Elastic Container Service) constantly polls the SQS queue.
6. **Process and Convert:** When the worker picks up a message, it starts a Docker container. This container pulls the raw video from the `raw_videos` S3 bucket and uses FFmpeg to transcode it into the HLS (HTTP Live Streaming) format. This creates multiple smaller video segments and a manifest file, which are ideal for adaptive streaming.
7. **Save Processed Video:** The newly processed HLS files are saved to a different S3 bucket (`processed_videos`).
8. **Update Database:** Finally, the worker updates the video's record in the PostgreSQL database with the new S3 key pointing to the processed HLS files.

## ⬇️ When Retrieving a Video

The retrieval process is optimized for speed and low-latency streaming by using a multi-layered caching strategy.

1. **Request Video:** The Flutter app requests a specific video from the FastAPI backend using an endpoint like `/video/:id`.
2. **Check Cache:** The backend first checks Redis (hosted on AWS ElastiCache) to see if the requested video's data is already cached. The diagram specifies an LRU (Least Recently Used) eviction policy, meaning it prioritizes caching the most popular videos.
3. **Cache Hit:** If the data is found in Redis (a "cache hit"), it's returned to the Flutter app immediately, resulting in a very fast response.
4. **Cache Miss & DB Query:** If the data is not in Redis (a "cache miss"), the backend queries the PostgreSQL database to retrieve the video's details and the location of its HLS manifest file in S3. The retrieved data is then stored in Redis for future requests.
5. **Stream via CDN:** The backend returns the video metadata and the streaming URL to the Flutter app. This URL points to the HLS manifest file in the `processed_videos` S3 bucket, which is delivered through AWS CloudFront. CloudFront acts as a Content Delivery Network (CDN), caching the video segments at edge locations around the world, ensuring fast, low-latency streaming for the end-user.
