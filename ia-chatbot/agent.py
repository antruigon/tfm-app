import logging

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

from config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL, MCP_SERVER_URL

logger = logging.getLogger(__name__)


@tool
def fallback_reply(user_message: str) -> str:
    """Responde cuando no hay herramientas MCP disponibles."""
    return f"He recibido tu mensaje: {user_message}"


def build_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=GROQ_MODEL,
        api_key=GROQ_API_KEY,
        base_url=GROQ_BASE_URL,
        temperature=0.3,
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
            (
                "system",
                "Eres un asistente DevOps del TFM. Responde en español, de forma breve y útil. "
                "Usa las herramientas MCP cuando ayuden a responder.",
            ),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=False, max_iterations=5)


async def run_agent(agent: AgentExecutor, user_text: str) -> str:
    result = await agent.ainvoke({"input": user_text})
    return str(result.get("output", "No he podido generar una respuesta."))
