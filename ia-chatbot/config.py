import os

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
MCP_SERVER_URL = os.environ.get(
    "MCP_SERVER_URL",
    "http://mcp-server.apps.svc.cluster.local:8000/mcp",
)
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_BASE_URL = os.environ.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
HEALTH_PORT = int(os.environ.get("HEALTH_PORT", "8080"))
