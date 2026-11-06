"""Only the explicit paper-compatibility tests see the frozen snapshot."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "reproduce/paper_backend"))
