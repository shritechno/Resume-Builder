import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.database import get_db
from app.services.template_service import get_active_templates


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _editor_context(template_slug: str = "") -> dict:
    return {
        "selected_template": template_slug,
        "initial_data": {
            "full_name": "",
            "email": "",
            "phone": "",
            "location": "",
            "summary": "",
            "skills": "",
            "experience": "",
            "education": "",
            "projects": "",
        },
    }


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    template_items = get_active_templates(db)
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "templates_list": template_items,
        },
    )


@router.get("/templates", response_class=HTMLResponse)
def template_gallery(request: Request, db: Session = Depends(get_db)):
    template_items = get_active_templates(db)
    return templates.TemplateResponse(
        request,
        "templates.html",
        {
            "request": request,
            "templates_list": template_items,
        },
    )


@router.get("/editor", response_class=HTMLResponse)
def editor(request: Request, template: str = "", db: Session = Depends(get_db)):
    template_items = get_active_templates(db)
    context = _editor_context(template)
    settings = get_settings()
    ai_configured = bool(settings.openai_api_key.strip())
    return templates.TemplateResponse(
        request,
        "editor.html",
        {
            "request": request,
            "templates_list": template_items,
            "selected_template": context["selected_template"],
            "initial_data": context["initial_data"],
            "initial_data_json": json.dumps(context["initial_data"]),
            "ai_configured": ai_configured,
        },
    )
