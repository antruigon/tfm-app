import os
import sys
from pathlib import Path

os.environ.setdefault("SLACK_BOT_TOKEN", "xoxb-test")
os.environ.setdefault("SLACK_APP_TOKEN", "xapp-test")
os.environ.setdefault("GROQ_API_KEY", "gsk-test")

sys.path.insert(0, str(Path(__file__).parent.parent))
