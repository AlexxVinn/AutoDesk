"""Workspace Assistant backend entrypoint."""

from __future__ import annotations

import argparse
import logging
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from workspace_assistant.api import router
from workspace_assistant.config import get_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Workspace Assistant",
        description="Phase 1 desktop productivity backend",
        version="0.1.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app


app = create_app()


def run() -> None:
    parser = argparse.ArgumentParser(description="Workspace Assistant backend")
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--config", default=None, help="Config directory path")
    args = parser.parse_args()

    if args.config:
        import os

        os.environ["WORKSPACE_ASSISTANT_CONFIG"] = args.config

    cfg = get_config().settings
    host = args.host or cfg.host
    port = args.port or cfg.port

    uvicorn.run(
        "workspace_assistant.main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    run()
