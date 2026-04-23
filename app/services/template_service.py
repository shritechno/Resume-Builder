from sqlalchemy.orm import Session

from app.models.entities import Template


SEED_TEMPLATES = [
    {
        "name": "Simple ATS",
        "slug": "simple-ats",
        "category": "Simple",
        "description": "A clean single-column layout focused on readability and ATS parsing.",
        "preview_image": "",
    },
    {
        "name": "Modern Professional",
        "slug": "modern-professional",
        "category": "Professional",
        "description": "A balanced layout for trending resumes with strong section hierarchy.",
        "preview_image": "",
    },
    {
        "name": "Executive Classic",
        "slug": "executive-classic",
        "category": "Executive",
        "description": "A polished format for experienced candidates who want a trusted style.",
        "preview_image": "",
    },
]


def seed_templates(db: Session) -> None:
    if db.query(Template).count():
        return

    for item in SEED_TEMPLATES:
        db.add(Template(**item))
    db.commit()


def get_active_templates(db: Session) -> list[Template]:
    return db.query(Template).filter(Template.is_active.is_(True)).order_by(Template.id.asc()).all()


def get_template_by_slug(db: Session, slug: str) -> Template | None:
    return db.query(Template).filter(Template.slug == slug, Template.is_active.is_(True)).first()
