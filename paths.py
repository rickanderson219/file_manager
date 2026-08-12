from pathlib import Path
import sys

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

LOG_FILE = BASE_DIR / "log.jsonl"
CONFIG_FILE = BASE_DIR / "config.json"