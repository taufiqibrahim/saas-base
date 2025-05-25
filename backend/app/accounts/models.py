import enum
import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import SecretStr, field_validator, model_validator
from sqlmodel import TIMESTAMP, Column, Enum, Field, Relationship, SQLModel

from app.organizations.models import Organization, OrganizationPublic


class AccountType(enum.Enum):
    USER = "user"
    SERVICE_ACCOUNT = "service-account"


class AccountBase(SQLModel):
    email: str = Field(unique=True, index=True)
    disabled: bool = False
    account_type: AccountType = Field(
        sa_column=Column(Enum(AccountType)), default=AccountType.USER
    )


class Account(AccountBase, table=True):
    __tablename__ = "account"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, unique=True, index=True)

    hashed_password: Optional[str]

    # List of organizations owned by this account
    organizations: list["Organization"] = Relationship(back_populates="account")

    # The profile record of this account
    profile: Optional["AccountProfile"] = Relationship(back_populates="account")

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP, onupdate=datetime.now(timezone.utc)),
    )


class AccountCreate(AccountBase):
    uid: Optional[uuid.UUID] = None
    full_name: str
    password: Optional[SecretStr] = None
    account_type: Optional[AccountType] = AccountType.USER

    @model_validator(mode="after")
    def validate_password_rules(cls, model):
        # Skip password checks for service accounts
        if model.account_type == AccountType.SERVICE_ACCOUNT:
            return model
        
        if not model.password:
            raise ValueError("Password is required for non-service accounts")
        
        password_value = model.password.get_secret_value()

        if len(password_value) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.islower() for c in password_value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isupper() for c in password_value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in password_value):
            raise ValueError("Password must contain at least one number")

        return model


class AccountPublic(AccountBase):
    pass


class AccountUpdate(SQLModel):
    id: int
    email: Optional[str] = None
    password: Optional[str] = None


class AccountDelete(SQLModel):
    id: int


# ******** AccountProfile *****************************************************
class AccountProfileBase(SQLModel):
    full_name: str


class AccountProfile(AccountProfileBase, table=True):
    __tablename__ = "account_profile"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, unique=True, index=True)

    # Relationship to Account
    account_id: Optional[int] = Field(
        default=None, foreign_key="account.id", unique=True
    )
    account: Optional["Account"] = Relationship(back_populates="profile")

    # AccountProfile attributes
    avatar: Optional[str]

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP, onupdate=datetime.now(timezone.utc)),
    )


# ******** AccountProfileMe *****************************************************
class AccountProfileMe(SQLModel):
    uid: uuid.UUID
    email: str
    avatar: str | None
    full_name: str | None
    organizations: list[OrganizationPublic]
