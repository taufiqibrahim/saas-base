import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import TIMESTAMP, Column, Field, Relationship, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    from app.organizations.models import Organization

from app.utils import generate_public_id


class ProjectBase(SQLModel):
    public_id: str = Field(
        default_factory=lambda: generate_public_id(prefix="project"),
        unique=True,
        index=True,
    )
    name: str = Field(index=True)
    description: Optional[str]
    is_default_project: Optional[bool] = False


class Project(ProjectBase, table=True):
    __tablename__ = "project"
    __table_args__ = (
        UniqueConstraint(
            "organization_id", "name", name=f"uq_{__tablename__}_organization"
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, unique=True, index=True)

    # Parent organization of this project
    organization_id: int = Field(foreign_key="organization.id")
    organization: Optional["Organization"] = Relationship(back_populates="projects")

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP, onupdate=datetime.now(timezone.utc)),
    )


class ProjectPublic(ProjectBase):
    uid: uuid.UUID | None
