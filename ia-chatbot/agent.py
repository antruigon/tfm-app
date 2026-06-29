import logging

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from openai import APIError

from config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL, MCP_SERVER_URL

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Eres un asistente DevOps del TFM. Responde en español, breve y útil. "
    "Tienes herramientas MCP (echo, ping). "
    "Usa echo solo si el usuario pide repetir o probar un mensaje. "
    "Usa ping solo si el usuario pide comprobar que MCP responde. "
    "Para el resto de preguntas responde directamente sin herramientas."
)


@tool
def fallback_reply(user_message: str) -> str:
    """Responde cuando no hay herramientas MCP disponibles."""
    return f"He recibido tu mensaje: {user_message}"


def build_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=GROQ_MODEL,
        api_key=GROQ_API_KEY,
        base_url=GROQ_BASE_URL,
        temperature=0,
    )


async def build_agent() -> AgentExecutor:
    llm = build_llm()
    tools = [fallback_reply]

    try:
        client = MultiServerMCPClient(
            {
                "mcp-server": {
                    "url": MCP_SERVER_URL,
                    "transport": "streamable_http",
                }
            }
        )
        mcp_tools = await client.get_tools()
        if mcp_tools:
            tools = mcp_tools
            logger.info("Cargadas %s herramientas MCP", len(mcp_tools))
    except Exception as exc:
        logger.warning("MCP no disponible, usando fallback: %s", exc)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        max_iterations=3,
        handle_parsing_errors=True,
    )


async def _fallback_llm_reply(user_text: str) -> str:
    llm = build_llm()
    response = await llm.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_text),
        ]
    )
    return str(response.content)


async def run_agent(agent: AgentExecutor, user_text: str) -> str:
    try:
        result = await agent.ainvoke({"input": user_text})
        return str(result.get("output", "No he podido generar una respuesta."))
    except APIError as exc:
        logger.warning("Groq tool-calling falló, respuesta directa: %s", exc)
        return await _fallback_llm_reply(user_text)
    except Exception as exc:
        logger.exception("Error en agente: %s", exc)
        return await _fallback_llm_reply(user_text)
