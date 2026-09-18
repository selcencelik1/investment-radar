import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_db_setting(name: str) -> str | None:
    value = os.getenv(name)

    if value:
        return value

    try:
        value = st.secrets.get(name)
    except FileNotFoundError:
        return None

    return str(value) if value is not None else None


DB_HOST = get_db_setting("DB_HOST")
DB_PORT = get_db_setting("DB_PORT")
DB_NAME = get_db_setting("DB_NAME")
DB_USER = get_db_setting("DB_USER")
DB_PASSWORD = get_db_setting("DB_PASSWORD")

missing = [
    name
    for name, value in {
        "DB_HOST": DB_HOST,
        "DB_PORT": DB_PORT,
        "DB_NAME": DB_NAME,
        "DB_USER": DB_USER,
        "DB_PASSWORD": DB_PASSWORD,
    }.items()
    if not value
]

if missing:
    raise RuntimeError(
        "Missing database settings: " + ", ".join(missing)
    )

DB_SSLMODE = get_db_setting("DB_SSLMODE") or "prefer"