import asyncio
from dataclasses import dataclass

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from agent import build_agent, run_agent
from config import SLACK_APP_TOKEN, SLACK_BOT_TOKEN
from health import start_health_server
from logging_config import APP_LOGGER, configure_logging
from utils import clean_mention

logger = configure_logging()


@dataclass
class SlackContext:
    user_id: str
    channel_id: str
    channel_type: str
    event_type: str

    def summary(self) -> str:
        return (
            f"usuario={self.user_id} canal={self.channel_id} "
            f"tipo={self.channel_type} evento={self.event_type}"
        )


app = AsyncApp(
    token=SLACK_BOT_TOKEN,
    request_verification_enabled=False,
)
_agent = None


async def get_agent():
    global _agent
    if _agent is None:
        _agent = await build_agent()
    return _agent


def _context_from_event(event: dict, event_type: str) -> SlackContext:
    return SlackContext(
        user_id=event.get("user", "desconocido"),
        channel_id=event.get("channel", "desconocido"),
        channel_type=event.get("channel_type", "desconocido"),
        event_type=event_type,
    )


async def _reply(user_text: str, say, ctx: SlackContext) -> None:
    logger.info("[SLACK] Mensaje recibido | %s | texto: %r", ctx.summary(), user_text)

    try:
        agent = await get_agent()
        response = await run_agent(agent, user_text, slack_ctx=ctx)
    except Exception:
        logger.exception("[SLACK] Error procesando mensaje | %s", ctx.summary())
        response = "Ha ocurrido un error interno. Inténtalo de nuevo."

    preview = response if len(response) <= 200 else f"{response[:200]}..."
    logger.info("[SLACK] Respuesta enviada | %s | texto: %r", ctx.summary(), preview)
    await say(response)


@app.event("app_mention")
async def handle_mention(event, say):
    ctx = _context_from_event(event, "app_mention")
    text = clean_mention(event.get("text", ""))
    if not text:
        await say("Hola, ¿en qué puedo ayudarte?")
        return
    await _reply(text, say, ctx)


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
    ctx = _context_from_event(event, "message_im")
    await _reply(text, say, ctx)


async def main():
    logger.info("[APP] Iniciando ia-chatbot (Socket Mode)")
    start_health_server()
    handler = AsyncSocketModeHandler(app, SLACK_APP_TOKEN)
    await handler.start_async()


if __name__ == "__main__":
    asyncio.run(main())
