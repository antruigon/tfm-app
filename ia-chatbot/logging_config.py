import logging

APP_LOGGER = "ia-chatbot"

_NOISY_LOGGERS = (
    "httpx",
    "httpcore",
    "mcp",
    "mcp.client",
    "mcp.client.streamable_http",
    "langchain",
    "langchain_core",
    "langchain_openai",
    "openai",
    "urllib3",
)


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )

    for name in _NOISY_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)

    return logging.getLogger(APP_LOGGER)
