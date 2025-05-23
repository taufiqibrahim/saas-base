import asyncio
import subprocess
import uuid

from fastapi import UploadFile
from pydantic import BaseModel, SecretStr
from sqlalchemy import inspect
from sqlmodel import Session, select, text

from app.apps.models import App
from app.apps.schemas import AppCreate
from app.apps.services import create_app
from app.auth.models import AccountType
from app.auth.services.account import create_api_key
from app.core.config import demo_settings, postgis_settings
from app.core.logging import get_logger, setup_logging
from app.database.session import engine
from app.files.services import handle_upload_minio
from app.geospatial_mapping.models import (
    BoundingBox,
    Dataset,
    DatasetCreate,
    DatasetUpdate,
)
from app.geospatial_mapping.services import (
    create_dataset,
    get_dataset_bbox,
    update_dataset,
)
from app.users.models import UserProfile
from app.users.schemas import AccountCreate, UserProfileCreate
from app.users.services import (
    create_user_account,
    create_user_profile,
    get_account_by_email,
)

setup_logging()
logger = get_logger(__name__)


def load_data(session: Session) -> None:

    users = [
        AccountCreate(
            uid="35662eb0-0e97-4bf5-9c7f-882e0e378295",
            email=demo_settings.FIRST_SUPERUSER_EMAIL,
            password=SecretStr(demo_settings.FIRST_SUPERUSER_PASSWORD),
            full_name=demo_settings.FIRST_SUPERUSER_EMAIL,
        ),
        AccountCreate(
            uid="6e98eb6a-5b96-4db0-9354-cd05dbf27d48",
            email=demo_settings.DEMO_USER_EMAIL,
            password=SecretStr(demo_settings.DEMO_USER_PASSWORD),
            full_name=demo_settings.DEMO_USER_EMAIL,
        ),
        AccountCreate(
            uid="f45f3aa0-b7cd-4191-a8cc-87b69a844018",
            email=demo_settings.DEMO_SERVICE_ACCOUNT_EMAIL,
            full_name=demo_settings.DEMO_SERVICE_ACCOUNT_EMAIL,
            account_type=AccountType.SERVICE_ACCOUNT,
        ),
    ]

    for u in users:
        logger.info(f"Creating user: {u.email}")
        db_account = get_account_by_email(db=session, email=u.email)
        if db_account:
            logger.info("Email already registered")
        else:
            created_account = create_user_account(db=session, account=u)
            profile_create = UserProfileCreate(
                account_id=created_account.id, full_name=u.full_name
            )
            create_user_profile(
                db=session, account_id=created_account.id, profile=profile_create
            )
            user_profile = session.exec(
                select(UserProfile).where(UserProfile.id == created_account.id)
            ).first()
            logger.info(f"User created: {user_profile}")

            custom_api_key = f"ak_{uuid.uuid4()}"
            create_api_key(
                db=session, account_id=created_account.id, api_key=custom_api_key
            )

    apps = [
        AppCreate(
            name="geospatial-mapping-app",
            description="A modular platform that enables users to upload geospatial datasets, \
                configure and run cloud-hosted spatial algorithms, and interactively visualize the results on a map",
        ),
    ]

    for a in apps:
        logger.info(f"Creating app: {a.name}")
        db_app = session.exec(select(App).where(App.name == a.name)).first()

        if not db_app:
            db_app = create_app(db=session, app=a)
            logger.info(f"App created: {db_app}")


def get_table_name(uid):
    pg_table = "u_" + str(uid).replace("-", "_")
    return pg_table


class DatasetLoadOgr(BaseModel):
    uid: str
    tmp_dir: str
    tmp_file_path: str


def ensure_id_column(session: Session, table_name: str):
    query = text(
        f"""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = :table_name AND column_name = 'id'
        ) THEN
            ALTER TABLE "{table_name}" ADD COLUMN id BIGSERIAL PRIMARY KEY;
        END IF;
    END;
    $$;
    """
    )
    session.exec(query.params(table_name=table_name))


def ogr2ogr_to_postgis(data: DatasetLoadOgr) -> DatasetLoadOgr:
    pg_table = get_table_name(str(data.uid))
    # Build the ogr2ogr command
    ogr2ogr_command = [
        "ogr2ogr",
        "-f",
        "PostgreSQL",
        f"PG:host={postgis_settings.POSTGIS_HOST} \
            port={postgis_settings.POSTGIS_PORT} \
            user={postgis_settings.POSTGIS_USER} \
            dbname={postgis_settings.POSTGIS_DB} \
            password={postgis_settings.POSTGIS_PASSWORD}",
        data.tmp_file_path,
        "-nln",
        pg_table,
        "-a_srs",
        "EPSG:4326",
        "-overwrite",
        "-lco",
        "GEOMETRY_NAME=geom",
    ]

    # Run the command
    try:
        subprocess.run(ogr2ogr_command, check=True)
        logger.info("Data loaded successfully into PostGIS.")
        return pg_table
    except subprocess.CalledProcessError as e:
        logger.error(f"ogr2ogr failed (code {e.returncode})")
        raise Exception


async def load_geospatial_mapping_data(session: Session) -> None:
    demo_account = get_account_by_email(db=session, email=demo_settings.DEMO_USER_EMAIL)
    datasets = [
        DatasetCreate(
            uid="19bea7c2-d17c-47b7-b88a-1fe5133cc1b6",
            account_id=demo_account.id,
            name="open_energy_sample",
            description="open_energy_sample",
            file_name="open_energy_sample.json",
            storage_backend="minio",
            storage_uri="",
            status="uploaded",
        ),
    ]

    for d in datasets:
        logger.info(f"Creating dataset {d.name} using demo data data/{d.file_name}")

        # upload to minio
        file_path = f"src/scripts/data/{d.file_name}"
        with open(file_path, "rb") as f:
            upload_file = UploadFile(filename=d.file_name, file=f)
            upload_response = await handle_upload_minio(file=upload_file, uid=d.uid)
            logger.info(upload_response)

        db_dataset = session.exec(
            select(Dataset).where(
                Dataset.account_id == demo_account.id, Dataset.name == d.name
            )
        ).first()
        if db_dataset:
            logger.info(f"Dataset {d.uid} already registered")
        else:
            d.storage_uri = upload_response["storage_uri"]

            # create Dataset record with status = 'uploaded'
            created_dataset = create_dataset(db=session, dataset=d)
            logger.info(f"Dataset created: {created_dataset.name}")

        # load dataset to postgis via ogr2ogr
        pg_table = ogr2ogr_to_postgis(
            DatasetLoadOgr(
                uid=str(d.uid),
                tmp_dir="src/scripts/data",
                tmp_file_path="src/scripts/data/open_energy_sample.json",
            )
        )

        # make sure id column is available on new table
        logger.info("Getting primary key column...")
        inspector = inspect(engine)
        schema = "public"
        pk_info = inspector.get_pk_constraint(pg_table, schema)
        pk_columns = pk_info.get("constrained_columns", [])
        primary_key_column = pk_columns[0]

        bbox = get_dataset_bbox(db=session, dataset_uid=d.uid)

        # update Dataset record status,bbox
        updated_dataset = update_dataset(
            db=session,
            dataset_uid=d.uid,
            account_id=d.account_id,
            dataset=DatasetUpdate(
                status="ready",
                primary_key_column=primary_key_column,
                bbox=BoundingBox(**bbox),
            ),
        )
        logger.info(f"updated_dataset {updated_dataset}")


def init() -> None:
    with Session(engine) as session:
        load_data(session)
        asyncio.run(load_geospatial_mapping_data(session))


if __name__ == "__main__":
    logger.info("Creating initial data...")
    init()
    logger.info("Initial data created")
