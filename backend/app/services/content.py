from fastapi import HTTPException
from sqlalchemy import select
from ..models import Content, ContentVersion, Finding, AuditLog
from ..db import now

def audit(db, role, action, content_id=None, detail=None, ai=False):
    db.add(AuditLog(content_id=content_id, role=role, action=action, detail=detail or {}, ai_involved=ai))

def create_content(db, title, channel, text, role='creator', source='manual'):
    item = Content(title=title, channel=channel, created_by_role=role)
    db.add(item)
    db.flush()
    db.add(ContentVersion(content_id=item.id, version_no=1, text=text, created_by_role=role, source=source))
    audit(db, role, 'content_created', item.id, {'source': source})
    db.flush()
    return item

def get_content(db, content_id):
    item = db.get(Content, content_id)
    if not item:
        raise HTTPException(404, 'Draft not found.')
    return item

def latest(db, content_id):
    return db.scalar(select(ContentVersion).where(ContentVersion.content_id == content_id).order_by(ContentVersion.version_no.desc()))

def findings_for(db, version_id):
    return list(db.scalars(select(Finding).where(Finding.version_id == version_id).order_by(Finding.start, Finding.id)))

def editable(item):
    if item.status not in {'draft', 'changes_requested'}:
        raise HTTPException(409, 'This draft is in the approval workflow. Ask a manager or reviewer to return it before editing.')

def add_version(db, item, text, role, source='manual'):
    editable(item)
    if not text.strip() or len(text) > 5000:
        raise HTTPException(422, 'Draft text must contain 1 to 5,000 characters.')
    previous = latest(db, item.id)
    version = ContentVersion(content_id=item.id, version_no=previous.version_no + 1, text=text, created_by_role=role, source=source)
    db.add(version)
    item.status, item.updated_at = 'draft', now()
    audit(db, role, 'version_created', item.id, {'version_no': version.version_no, 'source': source})
    db.flush()
    return version

def apply_text(text, findings):
    for finding in sorted(findings, key=lambda f: f.start, reverse=True):
        if finding.decision in {'accepted', 'edited'}:
            replacement = finding.replacement if finding.decision == 'accepted' else finding.edited_text
            if replacement is None:
                raise HTTPException(422, 'A selected finding has no replacement. Edit it first.')
            if text[finding.start:finding.end] != finding.quote:
                raise HTTPException(409, 'Finding offsets do not match this version. Run review again.')
            text = text[:finding.start] + replacement + text[finding.end:]
    return text
