# Libra AI Coworker

Production-ready multi-agent AI Coworker demo with a Next.js frontend on Vercel
and a FastAPI backend on Render. The app turns natural language requests into
visible, approval-gated workflows across realistic mock Gmail, Slack, and CRM
tools.

## What It Does

- Streams every workflow step to the UI with Server-Sent Events.
- Uses a Manager, Researcher, Analyst, Executor, and Safety flow.
- Searches realistic mock Gmail and Slack data.
- Requires human approval before every CRM update or email draft.
- Shows a Notion-inspired dark workspace with sidebar history, live logs, and markdown results.
- Uses NVIDIA-hosted GLM through an OpenAI-compatible client configuration.

## Project Structure

```text
libra_ai_coworker/
├── backend/                 FastAPI app for Render
│   ├── agents/              Orchestration and CrewAI configuration
│   ├── routers/             Workflow, SSE, and approval endpoints
│   ├── state/               In-memory workflow sessions
│   └── tools/               Mock Gmail, Slack, CRM, and email draft tools
├── frontend/                Next.js 14 App Router app for Vercel
│   ├── app/                 Workspace routes and global layout
│   ├── components/          Sidebar, workflow input/log, approval modal, result card
│   ├── hooks/               SSE workflow and approval state
│   └── lib/                 API client and shared TypeScript types
└── docs/                    Product and module PRDs
```

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload
```

Set `NVIDIA_API_KEY` in `backend/.env`. Do not commit real API keys.
Use Python 3.11 for parity with Render. On Windows, CrewAI's transitive
`chroma-hnswlib` dependency may require Microsoft C++ Build Tools; Render's
Linux runtime is the intended production target.

Health check:

```bash
curl http://localhost:8000/health
```

Expected:

```json
{"status":"ok","model":"zhipuai/glm-4v-flash"}
```

### Frontend

```bash
cd frontend
npm install
copy .env.local.example .env.local
npm run dev
```

Open `http://localhost:3000/workspace`.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Backend health and model metadata |
| `POST` | `/api/workflow/start` | Start a workflow with `{ "input": "..." }` |
| `GET` | `/api/workflow/{id}/stream` | SSE stream of workflow step events |
| `POST` | `/api/workflow/{id}/approve` | Submit `{ "decision": "approved" | "rejected" }` |
| `GET` | `/api/workflow/{id}/result` | Fetch final result and full step log |

SSE responses set `Cache-Control: no-cache` and `X-Accel-Buffering: no` for Render compatibility.

## Safety Model

The write tools are `update_crm` and `send_email_draft`. Both are flagged with
`requires_approval=True`, and the orchestrator always pauses before invoking
their implementation. The workflow does not continue until the frontend posts an
explicit approval or rejection. Rejections are logged and the workflow continues
without performing the write.

## Deploy Backend To Render

1. Create a new Render Web Service from this repository.
2. Set the root directory to `backend`.
3. Render can use `backend/render.yaml`, or configure manually:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Python runtime: `python-3.11.9` from `backend/runtime.txt`
4. Add environment variables:
   - `NVIDIA_API_KEY`: your NVIDIA API key
   - `ENVIRONMENT`: `production`
   - `FRONTEND_URL`: your Vercel production URL, for example `https://your-app.vercel.app`
5. Deploy and verify `/health`.

## Deploy Frontend To Vercel

1. Create a new Vercel project from this repository.
2. Set the root directory to `frontend`.
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL`: your Render backend URL, for example `https://libra-ai-backend.onrender.com`
4. Build command is `npm run build`; output directory is `.next`.
5. Deploy and open `/workspace`.

## Demo Prompts

- `Find emails from Acme Corp this week and add a CRM note summarizing their status.`
- `Summarize today's messages in the #sales channel and give me the key highlights.`
- `Research TechCorp across Gmail and Slack, draft a CRM note and a follow-up email.`

The first and third prompts will trigger the approval modal because they include write actions.

## Environment Checklist

Backend:

```text
NVIDIA_API_KEY=nvapi-your-key-here
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
```

Frontend:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Production Notes

- Replace mock tools with real API clients inside the marked `REAL API` blocks.
- Keep approval outside tool internals so every write path remains centrally gated.
- The current workflow store is process-local memory; use Redis or Postgres before running multiple backend replicas.
- Never use wildcard CORS in production. The backend allows localhost and Vercel preview/production origins.
- The dependency pins are adjusted from the original PRD where necessary because the older CrewAI stack has resolver conflicts with newer FastAPI and LangChain packages.
