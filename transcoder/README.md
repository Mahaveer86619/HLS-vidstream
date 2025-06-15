# Transcoder

Handles asynchronous video processing and conversion.

## Codebase Flow

- Polls AWS SQS for new video processing jobs.
- Downloads raw videos from S3 (`raw_videos` bucket).
- Uses FFmpeg to transcode videos into HLS format (segments + manifest).
- Uploads processed HLS files to S3 (`processed_videos` bucket).
- Updates the PostgreSQL database with processed video locations.
