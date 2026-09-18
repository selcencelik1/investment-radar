import os

import streamlit as st
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker


def get_database_url():
    url = os.getenv("DATABASE_URL")

    if not url:
        try:
            url = st.secrets.get("DATABASE_URL")
        except FileNotFoundError:
            url = None

    if url:
        # Neon adresinde belirtilen SSL seçenekleri korunur.
        if url.startswith("p-cold-recipe-b4n17f7k-pooler.c-6.us-east-2.aws.neon.tech"):
            url = url.replace(
                "postgresql://",
                "postgresql+psycopg://",
                1,
            )
        return url

    # Mac'teki mevcut yerel kurulum çalışmaya devam eder.
    from app.config import (
        DB_HOST,
        DB_NAME,
        DB_PASSWORD,
        DB_PORT,
        DB_SSLMODE,
        DB_USER,
    )

    return URL.create(
        drivername="postgresql+psycopg",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        database=DB_NAME,
        query={"sslmode": DB_SSLMODE},
    )


engine = create_engine(
    get_database_url(),
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)