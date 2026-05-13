"""FastAPI entry point for Libra AI Coworker."""

from __future__ import annotations

import os
import re
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agents.orchestrator import MODEL
from routers import approval, workflow
from state.workflow_manager import workflow_manager

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await workflow_manager.shutdown()


app = FastAPI(
    title="Libra AI Coworker API",
    version="1.0.0",
    lifespan=lifespan,
)

frontend_url = os.getenv("FRONTEND_URL")
allow_origins = ["https://*.vercel.app", "http://localhost:3000"]
if frontend_url:
    allow_origins.append(frontend_url)

regex_parts = [r"https://.*\.vercel\.app"]
if frontend_url:
    regex_parts.append(re.escape(frontend_url))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex="|".join(regex_parts),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(workflow.router)
app.include_router(approval.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "model": MODEL}
