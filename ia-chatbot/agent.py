import logging
import re
from dataclasses import dataclass

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

from config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL, MCP_SERVER_URL

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Eres un asistente DevOps del TFM. Responde en español, breve y útil. "
    "Puedes explicar que el usuario puede pedir 'ping' para probar MCP o "
    "'echo <texto>' para repetir un mensaje."
)


@dataclass
class ChatbotState:
    llm: ChatOpenAI
    mcp_tools: list[BaseTool]


def build_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=GROQ_MODEL,
        api_key=GROQ_API_KEY,
        base_url=GROQ_BASE_URL,
        temperature=0,
    )


async def build_agent() -> ChatbotState:
    llm = build_llm()
    mcp_tools: list[BaseTool] = []

    try:
        client = MultiServerMCPClient(
            {
                "mcp-server": {
                    "url": MCP_SERVER_URL,
                    "transport": "streamable_http",
                }
            }
        )
        tools = await client.get_tools()
        if tools:
            mcp_tools = tools
            logger.info("Cargadas %s herramientas MCP", len(mcp_tools))
    except Exception as exc:
        logger.warning("MCP no disponible: %s", exc)

    return ChatbotState(llm=llm, mcp_tools=mcp_tools)


def _tools_by_name(tools: list[BaseTool]) -> dict[str, BaseTool]:
    return {tool.name: tool for tool in tools}


def _wants_ping(user_text: str) -> bool:
    lowered = user_text.lower()
    return bool(
        re.search(r"\bping\b", lowered)
        or "comprueba mcp" in lowered
        or "comprobar mcp" in lowered
        or "prueba mcp" in lowered
    )


def _extract_echo_message(user_text: str) -> str:
    lowered = user_text.lower().strip()
    for prefix in ("echo ", "repite ", "repite: ", "repetir ", "repetir:"):
        if lowered.startswith(prefix):
            return user_text[len(prefix) :].strip()
    match = re.search(r"\becho\b[:\s]+(.+)", user_text, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return user_text.strip()


def _wants_echo(user_text: str) -> bool:
    lowered = user_text.lower()
    return "echo" in lowered or lowered.startswith("repite")


async def _invoke_mcp_tool(state: ChatbotState, user_text: str) -> str | None:
    if not state.mcp_tools:
        return None

    tools = _tools_by_name(state.mcp_tools)

    if _wants_ping(user_text) and "ping" in tools:
        result = await tools["ping"].ainvoke({})
        return str(result)

    if _wants_echo(user_text) and "echo" in tools:
        message = _extract_echo_message(user_text) or user_text
        result = await tools["echo"].ainvoke({"message": message})
        return str(result)

    return None


async def _llm_reply(state: ChatbotState, user_text: str) -> str:
    response = await state.llm.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_text),
        ]
    )
    return str(response.content)


async def run_agent(state: ChatbotState, user_text: str) -> str:
    try:
        mcp_result = await _invoke_mcp_tool(state, user_text)
        if mcp_result is not None:
            return mcp_result
        return await _llm_reply(state, user_text)
    except Exception as exc:
        logger.exception("Error en agente: %s", exc)
        return "No he podido procesar tu mensaje. Inténtalo de nuevo en unos segundos."
