import asyncio
import logging

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from agent import build_agent, run_agent
from config import SLACK_APP_TOKEN, SLACK_BOT_TOKEN
from health import start_health_server
from utils import clean_mention

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = AsyncApp(
    token=SLACK_BOT_TOKEN,
    # Socket Mode: eventos por WebSocket, no HTTP → no hace falta signing secret
    request_verification_enabled=False,
)
_agent = None


async def get_agent():
    global _agent
    if _agent is None:
        _agent = await build_agent()
    return _agent


async def _reply(user_text: str, say) -> None:
    try:
        agent = await get_agent()
        response = await run_agent(agent, user_text)
    except Exception as exc:
        logger.exception("Error respondiendo en Slack: %s", exc)
        response = "Ha ocurrido un error interno. Inténtalo de nuevo."
    await say(response)


@app.event("app_mention")
async def handle_mention(event, say):
    text = clean_mention(event.get("text", ""))
    if not text:
        await say("Hola, ¿en qué puedo ayudarte?")
        return
    await _reply(text, say)


@app.event("message")
async def handle_message(event, say):
    if event.get("subtype") is not None:
        return
    if event.get("bot_id"):
        return
    if event.get("channel_type") != "im":
        return
    text = event.get("text", "").strip()
    if not text:
        return
    await _reply(text, say)


async def main():
    start_health_server()
    handler = AsyncSocketModeHandler(app, SLACK_APP_TOKEN)
    await handler.start_async()


if __name__ == "__main__":
    asyncio.run(main())
