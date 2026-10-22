from datetime import datetime, date
from sqlalchemy import String, Text, JSON, ForeignKey, DateTime, Date, Boolean, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base, now

class KnowledgeItem(Base):
    __tablename__ = 'knowledge_items'
    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(30))
    code: Mapped[str] = mapped_column(String(30), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    text: Mapped[str] = mapped_column(Text)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)

class Content(Base):
    __tablename__ = 'contents'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    channel: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(30), default='draft')
    created_by_role: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class ContentVersion(Base):
    __tablename__ = 'content_versions'
    __table_args__ = (UniqueConstraint('content_id', 'version_no'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    content_id: Mapped[int] = mapped_column(ForeignKey('contents.id'))
    version_no: Mapped[int]
    text: Mapped[str] = mapped_column(Text)
    created_by_role: Mapped[str] = mapped_column(String(30))
    source: Mapped[str] = mapped_column(String(30), default='manual')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class Finding(Base):
    __tablename__ = 'findings'
    id: Mapped[int] = mapped_column(primary_key=True)
    version_id: Mapped[int] = mapped_column(ForeignKey('content_versions.id'))
    issue_type: Mapped[str] = mapped_column(String(80))
    severity: Mapped[str] = mapped_column(String(20))
    quote: Mapped[str] = mapped_column(Text)
    start: Mapped[int]
    end: Mapped[int]
    source_code: Mapped[str | None] = mapped_column(String(30), nullable=True)
    also_cites: Mapped[list] = mapped_column(JSON, default=list)
    reason: Mapped[str] = mapped_column(Text)
    replacement: Mapped[str | None] = mapped_column(Text, nullable=True)
    replacement_hint: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    verification: Mapped[str] = mapped_column(String(20), default='verified')
    origin: Mapped[str] = mapped_column(String(20), default='rule')
    requires_reviewer: Mapped[bool] = mapped_column(Boolean, default=False)
    decision: Mapped[str] = mapped_column(String(20), default='pending')
    edited_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_by_role: Mapped[str | None] = mapped_column(String(20), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class Comment(Base):
    __tablename__ = 'comments'
    id: Mapped[int] = mapped_column(primary_key=True)
    content_id: Mapped[int] = mapped_column(ForeignKey('contents.id'))
    role: Mapped[str] = mapped_column(String(30))
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id: Mapped[int] = mapped_column(primary_key=True)
    content_id: Mapped[int | None] = mapped_column(ForeignKey('contents.id'), nullable=True)
    role: Mapped[str] = mapped_column(String(30))
    action: Mapped[str] = mapped_column(String(80))
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
    ai_involved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class ReviewCache(Base):
    __tablename__ = 'review_cache'
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    result: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class AIUsage(Base):
    __tablename__ = 'ai_usage'
    id: Mapped[int] = mapped_column(primary_key=True)
    model: Mapped[str] = mapped_column(String(100))
    tokens: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
