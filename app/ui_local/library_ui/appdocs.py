from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import ChoiceLoader, FileSystemLoader

from .routes import configure_templates, router
from .runtime.ui_paths import static_dir, templates_dir
from .workspace.routes_workspace import configure_workspace_templates, router as workspace_router

app = FastAPI(title="ASSISCLUE_KNOWLEDGE_LIBRARY_UI")

app.mount("/static", StaticFiles(directory=str(static_dir())), name="static")
app.mount("/info_assets", StaticFiles(directory=str(Path(__file__).resolve().parents[3] / "info")), name="info_assets")

main_templates = templates_dir()
workspace_templates = Path(__file__).resolve().parent / "workspace" / "templates"

templates = Jinja2Templates(directory=str(main_templates))
templates.env.loader = ChoiceLoader(
    [
        FileSystemLoader(str(main_templates)),
        FileSystemLoader(str(workspace_templates)),
    ]
)

configure_templates(templates)
configure_workspace_templates(templates)

app.include_router(router)
app.include_router(workspace_router)
