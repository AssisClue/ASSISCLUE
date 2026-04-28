from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .services import LibraryUiService
from .view_models import (
    build_area_browser_vm,
    build_area_vm,
    build_file_vm,
    build_home_vm,
    build_system_file_vm,
)

router = APIRouter()
service = LibraryUiService()
templates: Jinja2Templates | None = None


def configure_templates(value: Jinja2Templates) -> None:
    global templates
    templates = value


@router.get("/")
async def library_home(
    request: Request,
    search: str = "",
    extension: str = "",
    root_id: str = "",
):
    if templates is None:
        raise RuntimeError("Templates not configured.")

    payload = service.get_home_payload(
        search=search,
        extension=extension,
        root_id=root_id,
    )
    vm = build_home_vm(payload)
    context = {
        "request": request,
        "page_title": "Knowledge Library",
        "page_heading": "Knowledge Library Explorer",
        "page_tagline": "Browse user library files, open previews, and run summarize, index, or promote actions from one visual workspace.",
        "current_section": "home",
        **vm,
    }
    return templates.TemplateResponse(request, "library_home.html", context)


@router.get("/file/{item_id}")
async def library_file(request: Request, item_id: str):
    if templates is None:
        raise RuntimeError("Templates not configured.")

    payload = service.get_file_payload(item_id=item_id)
    vm = build_file_vm(payload)
    context = {
        "request": request,
        "page_title": "Library File",
        "page_heading": "Library File Detail",
        "page_tagline": "Inspect a mapped library file and see its current summary, index, and memory promotion state.",
        "current_section": "home",
        **vm,
    }
    return templates.TemplateResponse(request, "library_file.html", context)


@router.get("/area/{area_key}")
async def library_area(request: Request, area_key: str):
    if templates is None:
        raise RuntimeError("Templates not configured.")

    payload = service.get_area_payload(area_key)
    vm = build_area_vm(payload)
    context = {
        "request": request,
        "page_title": "System Area",
        "page_heading": "System Area Explorer",
        "page_tagline": "Choose one root folder from this app area, then browse its real folders and files with clear boundaries.",
        "current_section": "areas",
        **vm,
    }
    return templates.TemplateResponse(request, "library_area.html", context)


@router.get("/area/{area_key}/browse")
async def library_area_browse(
    request: Request,
    area_key: str,
    current_path: str,
    search: str = "",
    extension: str = "",
    entry_type: str = "",
):
    if templates is None:
        raise RuntimeError("Templates not configured.")

    payload = service.get_area_browser_payload(
        area_key,
        current_path=current_path,
        search=search,
        extension=extension,
        entry_type=entry_type,
    )
    vm = build_area_browser_vm(payload)
    context = {
        "request": request,
        "page_title": "Area Folder Browser",
        "page_heading": "Area Folder Browser",
        "page_tagline": "Browse one real folder at a time, with breadcrumbs, filters, and direct file preview.",
        "current_section": "areas",
        **vm,
    }
    return templates.TemplateResponse(request, "area_browser.html", context)


@router.get("/system-file")
async def system_file(
    request: Request,
    area_key: str = Query(...),
    file_path: str = Query(...),
):
    if templates is None:
        raise RuntimeError("Templates not configured.")

    try:
        payload = service.get_system_file_payload(area_key=area_key, file_path=file_path)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    vm = build_system_file_vm(payload)
    context = {
        "request": request,
        "page_title": "System File",
        "page_heading": "System File Detail",
        "page_tagline": "Preview a real runtime or source file from one of the app areas.",
        "current_section": "areas",
        **vm,
    }
    return templates.TemplateResponse(request, "system_file.html", context)



@router.post("/actions/mark/library/{item_id}")
async def mark_library_file(item_id: str):
    service.mark_library_file(item_id)
    return RedirectResponse(url=f"/file/{item_id}", status_code=303)


@router.post("/actions/mark/system")
async def mark_system_file(
    area_key: str = Query(...),
    file_path: str = Query(...),
):
    service.mark_system_file(area_key, file_path)
    return RedirectResponse(
        url=f"/system-file?area_key={area_key}&file_path={file_path}",
        status_code=303,
    )


@router.get("/raw-file/{item_id}")
async def raw_file(item_id: str):
    try:
        item = service.get_item_by_id(item_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    path = Path(str(item.get("absolute_path", "")).strip())
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found.")

    return FileResponse(path=path, filename=path.name, content_disposition_type="inline")


@router.get("/system-raw-file")
async def system_raw_file(
    area_key: str = Query(...),
    file_path: str = Query(...),
):
    try:
        payload = service.get_system_file_payload(area_key=area_key, file_path=file_path)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    path = Path(str(payload["entry"]["path"]).strip())
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found.")

    return FileResponse(path=path, filename=path.name, content_disposition_type="inline")


@router.post("/actions/scan")
async def scan_library():
    service.scan_all()
    return RedirectResponse(url="/", status_code=303)


@router.post("/actions/summarize/{item_id}")
async def summarize_file(item_id: str):
    service.summarize_file(item_id)
    return RedirectResponse(url=f"/file/{item_id}", status_code=303)


@router.post("/actions/index/{item_id}")
async def index_file(item_id: str):
    service.index_file(item_id)
    return RedirectResponse(url=f"/file/{item_id}", status_code=303)


@router.post("/actions/promote/{item_id}")
async def promote_file(item_id: str):
    service.promote_file(item_id)
    return RedirectResponse(url=f"/file/{item_id}", status_code=303)