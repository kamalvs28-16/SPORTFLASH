import time
import json
import asyncio
from typing import Dict, Any, AsyncGenerator, Optional
from collections import deque

from api.db import get_db_connection
from pipeline.orchestrator import run_full_pipeline


class JobManager:
    """
    Background Task Manager & Server-Sent Events (SSE) Progress Broadcaster.
    Tracks job status, current frame processing progress, and errors.
    """

    def __init__(self):
        self.active_jobs: Dict[str, Dict[str, Any]] = {}
        self.event_queues: Dict[str, list] = {}

    def create_job(self, job_id: str, match_id: str, video_path: str) -> Dict[str, Any]:
        job_state = {
            "job_id": job_id,
            "match_id": match_id,
            "video_path": video_path,
            "status": "queued",
            "progress": 0,
            "step_name": "Queued",
            "details": "Job queued for execution",
            "current_frame": 0,
            "total_frames": 0,
            "error": None
        }
        self.active_jobs[job_id] = job_state
        return job_state

    def update_job_progress(self, job_id: str, progress: int, step_name: str, details: str, current_frame: int = 0, total_frames: int = 0):
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job.update({
                "status": "processing" if progress < 100 else "completed",
                "progress": progress,
                "step_name": step_name,
                "details": details,
                "current_frame": current_frame,
                "total_frames": total_frames
            })

    async def sse_event_generator(self, job_id: str) -> AsyncGenerator[str, None]:
        """
        Streams Server-Sent Events (SSE) JSON payloads to frontend client.
        """
        while True:
            job = self.active_jobs.get(job_id)
            if not job:
                yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
                break

            yield f"data: {json.dumps(job)}\n\n"

            if job["status"] in ["completed", "failed"]:
                break

            await asyncio.sleep(0.5)


job_manager = JobManager()
