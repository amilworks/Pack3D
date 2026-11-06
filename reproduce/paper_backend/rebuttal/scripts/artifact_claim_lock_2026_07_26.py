#!/usr/bin/env python3
"""Cross-process claim lock for collision-safe dated rebuttal runs."""

from __future__ import annotations

from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import socket
from typing import TextIO


def acquire_artifact_claim(
    root: Path,
    *,
    phase: str,
    run_id: str,
) -> TextIO:
    """Acquire a nonblocking process-lifetime lock for one run identity."""
    identity = f"{phase}\0{run_id}".encode()
    digest = hashlib.sha256(identity).hexdigest()
    lock_dir = root / "results/raw/.rebuttal_claim_locks"
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_path = lock_dir / f"{digest}.lock"
    handle = lock_path.open("a+", encoding="utf-8")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        handle.seek(0)
        owner = handle.read().strip() or "owner metadata unavailable"
        handle.close()
        raise RuntimeError(
            "Another process already owns this rebuttal run identity: "
            f"phase={phase}, run_id={run_id}; {owner}"
        ) from exc
    handle.seek(0)
    handle.truncate()
    handle.write(
        json.dumps(
            {
                "phase": phase,
                "run_id": run_id,
                "pid": os.getpid(),
                "hostname": socket.gethostname(),
                "acquired_utc": datetime.now(timezone.utc).isoformat(),
            },
            sort_keys=True,
        )
        + "\n"
    )
    handle.flush()
    return handle
