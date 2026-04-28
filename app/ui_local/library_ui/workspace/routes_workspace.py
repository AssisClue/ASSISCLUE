from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from .services_workspace import WorkspaceUiService

router = APIRouter()
service = WorkspaceUiService()
templates: Jinja2Templates | None = None


def configure_workspace_templates(value: Jinja2Templates) -> None:
    global templates
    templates = value


@router.get("/workspace")
async def workspace_home(request: Request):
    if templates is None:
        raise RuntimeError("Workspace templates not configured.")

    payload = service.get_workspace_payload()
    context = {
        "request": request,
        "page_title": "Workspace",
        "page_heading": "Marked Workspace",
        "page_tagline": "This page shows only the files you marked for focused work, grouped by stage.",
        "current_section": "workspace",
        **payload,
    }
    return templates.TemplateResponse(request, "workspace_home.html", context)


@router.post("/workspace/actions/unmark/{mark_id}")
async def workspace_unmark(mark_id: str):
    service.unmark(mark_id)
    return RedirectResponse(url="/workspace", status_code=303)


@router.post("/workspace/actions/link/{mark_id}")
async def workspace_link(mark_id: str):
    try:
        service.link_mark_to_library(mark_id)
    except Exception:
        pass
    return RedirectResponse(url="/workspace", status_code=303)


@router.post("/workspace/actions/summarize/{mark_id}")
async def workspace_summarize(mark_id: str):
    try:
        service.summarize_mark(mark_id)
    except Exception:
        pass
    return RedirectResponse(url="/workspace", status_code=303)


@router.post("/workspace/actions/index/{mark_id}")
async def workspace_index(mark_id: str):
    try:
        service.index_mark(mark_id)
    except Exception:
        pass
    return RedirectResponse(url="/workspace", status_code=303)


@router.post("/workspace/actions/promote/{mark_id}")
async def workspace_promote(mark_id: str):
    try:
        service.promote_mark(mark_id)
    except Exception:
        pass
    return RedirectResponse(url="/workspace", status_code=303)