import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.entities import ResumeDraft
from app.models.schemas import AIImproveRequest, ResumeDownloadRequest
from app.services.ai_service import AIService
from app.services.ats_service import extract_resume_text
from app.services.docx_service import build_resume_doc
from app.services.template_service import get_template_by_slug


router = APIRouter(prefix="/api", tags=["api"])
ai_service = AIService()


@router.post("/improve")
async def improve_content(payload: AIImproveRequest):
    improved = await ai_service.improve_content(payload.action, payload.content)
    return {"result": improved}


@router.post("/download")
def download_resume(payload: ResumeDownloadRequest, db: Session = Depends(get_db)):
    template = get_template_by_slug(db, payload.template_slug)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    draft = ResumeDraft(
        template_id=template.id,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        location=payload.location,
        summary=payload.summary,
        skills_json=json.dumps(payload.skills),
        experience_json=json.dumps(payload.experience),
        education_json=json.dumps(payload.education),
        projects_json=json.dumps(payload.projects),
    )
    db.add(draft)
    db.commit()

    content = build_resume_doc(template.name, template.slug, payload)
    filename = f"{payload.full_name.strip().replace(' ', '_') or 'resume'}_{template.slug}.docx"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        iter([content]),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )


@router.post("/ats-check")
async def ats_check_resume(file: UploadFile = File(...), target_role: str = Form(default="")):
    resume_text = await extract_resume_text(file)
    report = await ai_service.check_ats_resume(resume_text=resume_text, target_role=target_role.strip())
    return {"result": report}
