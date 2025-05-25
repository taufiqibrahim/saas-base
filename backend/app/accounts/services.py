import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional

from fastapi import HTTPException
from sqlmodel import select

from app.accounts.models import (
    Account,
    AccountCreate,
    AccountDelete,
    AccountProfile,
    AccountProfileMe,
    AccountUpdate,
)
from app.auth.services.security import get_password_hash
from app.core.exceptions import (
    APINotImplementedError,
    EmailAlreadyExistsException,
)
from app.core.logging import get_logger, setup_logging
from app.organizations.models import Organization
from app.projects.models import Project

setup_logging()
logger = get_logger(__name__)


async def create_account(db: AsyncSession, account: AccountCreate) -> Account:
    logger.debug(f"Creating user account: {account.email}")
    try:
        async with db.begin():
            # Check if email already exists
            existing_account = await get_account_by_email(db, account.email)
            if existing_account:
                raise EmailAlreadyExistsException

            # Create the account
            hashed_password = (
                get_password_hash(account.password.get_secret_value()) if account.password else None
            )

            db_account = Account(
                email=account.email.lower(),
                hashed_password=hashed_password,
                disabled=account.disabled,
                account_type=account.account_type,
                uid=account.uid if account.uid else uuid.uuid4(),
            )

            db.add(db_account)
            await db.flush()

            # Create account profile
            db_account_profile = AccountProfile(
                account=db_account, full_name=account.full_name
            )
            db.add(db_account_profile)
            await db.flush()

            # Create default organization
            db_account_org = Organization(
                account=db_account,
                name="Default org",
                description="Default organization",
                is_default_org=True,
            )
            db.add(db_account_org)
            await db.flush()

            # Create default project
            db_account_project = Project(
                organization=db_account_org,
                name="Default project",
                description="Default project",
                is_default_project=True,
            )
            db.add(db_account_project)
            await db.flush()

            logger.debug(f"Created user account: {db_account.email.lower()}")
    except Exception as e:
        logger.error(str(e))
        raise

    return db_account


async def update_account(db: AsyncSession, account: AccountUpdate) -> Account:
    db_account = db.execute(select(Account).where(Account.id == account.id)).scalars().first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    account_data = account.model_dump(exclude_unset=True)
    for key, value in account_data.items():
        if key == "password":
            db_account.hashed_password = get_password_hash(value)
        else:
            setattr(db_account, key, value)

    db.add(db_account)
    db.commit()
    db.refresh(db_account)

    return db_account


async def delete_account(db: AsyncSession, account: AccountDelete) -> Account:
    raise APINotImplementedError


async def get_account(db: AsyncSession, account_id: int) -> Optional[Account]:
    account = db.execute(select(Account).where(Account.id == account_id)).scalars().first()
    return account


async def get_account_profile(db: AsyncSession, account_id: int):
    result = await db.execute(
        select(Account)
        .options(
            selectinload(Account.profile),
            selectinload(Account.organizations).selectinload(Organization.projects),
        )
        .where(Account.id == account_id)
    )
    account = result.scalar_one_or_none()

    if not account or not account.profile:
        return None

    profile = account.profile

    return AccountProfileMe(
        uid=account.uid,
        email=account.email,
        avatar=profile.avatar,
        disabled=account.disabled,
        full_name=profile.full_name,
        organizations=account.organizations,
        created_at=profile.created_at.isoformat(),
        updated_at=profile.updated_at.isoformat(),
    )


async def get_account_by_email(db: AsyncSession, email: str) -> Optional[Account]:
    logger.debug("get_account_by_email")
    result = await db.execute(select(Account).where(Account.email == email.lower()))
    return result.scalars().first()


# async def get_account_by_api_key(db: Session, api_key: str) -> Optional[Account]:
#     result = db.execute(
#         select(Account).join(APIKey).where(APIKey.key == api_key, APIKey.is_active)
#     ).scalars().first()
#     return result


async def get_accounts(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Account]:
    result = db.execute(select(Account).offset(skip).limit(limit))
    return result.scalars().all()
