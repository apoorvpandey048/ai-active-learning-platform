"""Monitor backend logs for HF model download/load progress, poll /models/status
and fetch a YouTube transcript when models are ready.

Usage (PowerShell example):
  & .\venv311\Scripts\Activate.ps1
  python backend\monitor_and_fetch.py --yt https://www.youtube.com/watch?v=znF2U_3Z210

The script will tail `backend/backend.err` (default) and poll
http://localhost:5000/models/status. When both summarizer and generator
report ready, it will fetch the transcript (using youtube-transcript-api if
installed) and write a prepared transcript file under `backend/transcripts/`.

The script includes retries, exponential backoff, and logging.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import threading
import time
from datetime import datetime
from typing import Callable, Optional

import requests

LOG = logging.getLogger('monitor')
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')


def tail_file(path: str, stop_event: threading.Event, on_line: Callable[[str], None], poll_interval: float = 0.5):
    """Tail a file and call on_line for each new line until stop_event is set."""
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            # Seek to end
            f.seek(0, os.SEEK_END)
            while not stop_event.is_set():
                line = f.readline()
                if not line:
                    time.sleep(poll_interval)
                    continue
                on_line(line.rstrip('\n'))
    except FileNotFoundError:
        LOG.warning('Log file %s not found (will rely on /models/status polling)', path)
        return
    except Exception as e:
        LOG.exception('Error while tailing file: %s', e)


def poll_models_status(status_url: str, timeout: int = 3600, interval: float = 5.0) -> Optional[dict]:
    """Poll the backend /models/status endpoint until both models are ready or timeout.

    Returns the final JSON status on success, or None on timeout/failure.
    """
    start = time.time()
    backoff = 1.0
    while True:
        try:
            resp = requests.get(status_url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            LOG.info('models/status => transformers_available=%s summarizer_ready=%s generator_ready=%s',
                     data.get('transformers_available'), data.get('summarizer_ready'), data.get('generator_ready'))
            if data.get('transformers_available') and data.get('summarizer_ready') and data.get('generator_ready'):
                return data
        except requests.RequestException as e:
            LOG.warning('Failed to reach %s: %s', status_url, e)

        elapsed = time.time() - start
        if elapsed > timeout:
            LOG.error('Timeout while waiting for models to become ready (waited %ds)', timeout)
            return None

        time.sleep(interval)
        # gentle backoff of polling interval (but keep it bounded)
        backoff = min(backoff * 1.1, 5.0)


def extract_video_id(url: str) -> str:
    """Extract YouTube video id from a URL or return the input if it looks like an id."""
    m = re.search(r'(?:v=|youtu\.be/)([A-Za-z0-9_-]{6,})', url)
    return m.group(1) if m else url


def fetch_transcript_local(vid: str) -> Optional[str]:
    """Try to fetch a transcript using youtube-transcript-api if installed.

    Returns the transcript text or None on failure.
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        LOG.info('Using youtube-transcript-api to fetch transcript for %s', vid)
        raw = YouTubeTranscriptApi.get_transcript(vid)
        text = ' '.join([t.get('text', '') for t in raw])
        return text
    except Exception as e:
        LOG.warning('youtube-transcript-api not available or failed: %s', e)
        return None


def fetch_transcript_via_backend(fetch_url: str, full_video_url: str, timeout: int = 30) -> Optional[str]:
    """Ask the running backend to fetch the transcript (backend has a /fetch-transcript endpoint).

    This will fallback to the backend's mocked transcript if youtube-transcript-api is not installed there.
    """
    try:
        LOG.info('Requesting backend to fetch transcript for %s', full_video_url)
        resp = requests.post(fetch_url, json={'url': full_video_url}, timeout=timeout)
        resp.raise_for_status()
        j = resp.json()
        return j.get('transcript')
    except Exception as e:
        LOG.exception('Backend transcript fetch failed: %s', e)
        return None


def prepare_and_save_transcript(transcript: str, out_dir: str, vid: str) -> str:
    """Perform lightweight cleaning/preparation and save to disk. Returns file path."""
    os.makedirs(out_dir, exist_ok=True)
    # Simple normalization
    text = transcript.replace('\r', ' ').replace('\n', ' ').strip()
    # Optionally truncate or chunk later; for now save full prepared transcript
    fname = f'transcript_{vid}_{int(time.time())}.txt'
    fpath = os.path.join(out_dir, fname)
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(text)
    LOG.info('Prepared transcript saved to %s', fpath)
    return fpath


def main():
    parser = argparse.ArgumentParser(description='Monitor backend logs, wait for HF models, and fetch YouTube transcript')
    parser.add_argument('--log-path', default=os.path.join('backend', 'backend.err'), help='Path to backend error log to tail')
    parser.add_argument('--status-url', default='http://localhost:5000/models/status', help='Backend /models/status URL')
    parser.add_argument('--fetch-url', default='http://localhost:5000/fetch-transcript', help='Backend /fetch-transcript URL')
    parser.add_argument('--yt', required=True, help='YouTube video URL or video id to fetch transcript for')
    parser.add_argument('--timeout', type=int, default=60*60, help='Max seconds to wait for models to become ready')
    parser.add_argument('--poll-interval', type=float, default=5.0, help='Seconds between /models/status polls')
    parser.add_argument('--out-dir', default=os.path.join('backend', 'transcripts'), help='Directory to write prepared transcripts')
    args = parser.parse_args()

    stop_event = threading.Event()
    # Simple shared flags updated from the log tail
    flags = {'summarizer_ready': False, 'generator_ready': False}

    def on_line(line: str):
        LOG.debug('log: %s', line)
        low = line.lower()
        if 'summarizer ready' in low:
            flags['summarizer_ready'] = True
            LOG.info('Detected summarizer ready in logs')
        if 'generator ready' in low:
            flags['generator_ready'] = True
            LOG.info('Detected generator ready in logs')
        # Detect download progress lines often emitted by HF/transformers
        if 'downloading pytorch_model.bin' in low or 'downloaded pytorch_model.bin' in low:
            LOG.info('Model download progress: %s', line.strip())

    # Start tailing logs in a background thread
    tail_thread = threading.Thread(target=tail_file, args=(args.log_path, stop_event, on_line), daemon=True)
    tail_thread.start()

    # Poll /models/status until both ready or until flags from logs indicate ready
    start = time.time()
    status = None
    try:
        while True:
            # First consult log-detected flags — if both True, we can skip polling
            if flags['summarizer_ready'] and flags['generator_ready']:
                LOG.info('Both models reported ready from log monitoring')
                # But still confirm via HTTP status endpoint once
                try:
                    status = requests.get(args.status_url, timeout=10).json()
                    LOG.info('Confirmed /models/status: %s', json.dumps(status))
                except Exception as e:
                    LOG.warning('Failed to confirm /models/status after log signal: %s', e)
                    status = None
                break

            # Poll HTTP endpoint for definitive readiness
            try:
                resp = requests.get(args.status_url, timeout=10)
                if resp.status_code == 200:
                    status = resp.json()
                    LOG.info('Polled /models/status => transformers_available=%s summarizer_ready=%s generator_ready=%s',
                             status.get('transformers_available'), status.get('summarizer_ready'), status.get('generator_ready'))
                    if status.get('transformers_available') and status.get('summarizer_ready') and status.get('generator_ready'):
                        LOG.info('Models are ready per /models/status')
                        break
                else:
                    LOG.warning('/models/status returned %s', resp.status_code)
            except requests.RequestException as e:
                LOG.debug('HTTP poll failed: %s', e)

            if time.time() - start > args.timeout:
                LOG.error('Timed out waiting for models to be ready after %ds', args.timeout)
                stop_event.set()
                return

            time.sleep(args.poll_interval)

        # At this point models are ready (or at least signaled ready): proceed to fetch transcript
        vid = extract_video_id(args.yt)
        LOG.info('Fetching transcript for video id=%s', vid)

        # Try local youtube-transcript-api first
        transcript = fetch_transcript_local(vid)
        if not transcript:
            # Fallback to backend endpoint which itself may call youtube-transcript-api or return mock
            transcript = fetch_transcript_via_backend(args.fetch_url, args.yt)

        if not transcript:
            LOG.error('Failed to obtain transcript for %s', args.yt)
            stop_event.set()
            return

        # Prepare and save transcript
        out_path = prepare_and_save_transcript(transcript, args.out_dir, vid)
        LOG.info('Transcript preparation completed: %s', out_path)

    finally:
        stop_event.set()
        tail_thread.join(timeout=1.0)


if __name__ == '__main__':
    main()
