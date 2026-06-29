# ia-chatbot

Chatbot Slack con [Bolt for Python](https://docs.slack.dev/tools/bolt-python/) + LangChain + Groq + herramientas MCP.

## Comportamiento

- Responde cuando **mencionan** al bot en un canal (`app_mention`).
- Responde en **mensajes directos** (DM) a la app.

Usa **Socket Mode** (`xapp-` + `xoxb-`), sin necesidad de URL pública.

## LLM: Groq

El modelo se ejecuta en la API de [Groq](https://console.groq.com) (no hay que desplegar infraestructura de IA).

- API compatible con OpenAI: `https://api.groq.com/openai/v1`
- Modelo por defecto: `llama-3.1-8b-instant` (tier gratuito generoso para el TFM)

## Configuración en Slack

En [api.slack.com/apps](https://api.slack.com/apps):

1. **Socket Mode** → activado.
2. **OAuth & Permissions** → scopes del bot:
   - `app_mentions:read`
   - `chat:write`
   - `im:history`
   - `im:read`
3. **Event Subscriptions** → activado, suscribir:
   - `app_mention`
   - `message.im`
4. Reinstalar la app en el workspace tras cambiar scopes.

## Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `SLACK_BOT_TOKEN` | `xoxb-...` |
| `SLACK_APP_TOKEN` | `xapp-...` |
| `GROQ_API_KEY` | `gsk_...` desde [console.groq.com](https://console.groq.com) |
| `GROQ_MODEL` | Por defecto: `llama-3.1-8b-instant` |
| `GROQ_BASE_URL` | Por defecto: `https://api.groq.com/openai/v1` |
| `MCP_SERVER_URL` | Por defecto: `http://mcp-server.apps.svc.cluster.local:8000/mcp` |

## Secret en Kubernetes

```powershell
cd ..\tfm-charts
$env:SLACK_BOT_TOKEN = "xoxb-..."
$env:SLACK_APP_TOKEN = "xapp-..."
$env:GROQ_API_KEY = "gsk-..."
.\scripts\create-ia-chatbot-secret.ps1
kubectl rollout restart deployment ia-chatbot -n apps
```
