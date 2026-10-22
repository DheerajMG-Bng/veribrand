from fastapi import HTTPException
from ..db import now
from .content import latest, findings_for, audit

def submit_content(db, item, role):
    if item.status not in {'draft','changes_requested'}:
        raise HTTPException(409, 'Only a draft or returned content can be submitted.')
    version=latest(db,item.id)
    if not version.reviewed_at:
        raise HTTPException(409, 'Review the latest version before submitting.')
    findings=findings_for(db,version.id)
    if any(f.severity=='high' and f.decision=='pending' for f in findings):
        raise HTTPException(409, 'Decide every high-severity finding before submitting.')
    if any(f.decision in {'accepted','edited'} for f in findings):
        raise HTTPException(409, 'Apply your accepted or edited fixes, then review the new version before submitting.')
    item.status,item.updated_at='in_review',now()
    audit(db,role,'submitted',item.id,{'version':version.version_no})

def approve_content(db,item,role):
    if item.status!='in_review':
        raise HTTPException(409,'Only content awaiting manager review can be approved.')
    version=latest(db,item.id)
    risk=any(f.requires_reviewer for f in findings_for(db,version.id))
    item.status='pending_reviewer' if risk else 'approved'
    item.updated_at=now()
    audit(db,role,'manager_approved',item.id,{'status':item.status,'version':version.version_no})
