from sqlalchemy import text

from app.database.connection import engine


with engine.connect() as connection:
    result = connection.execute(
        text("SELECT current_user, current_database()")
    )

    current_user, current_database = result.one()

    print(f"Kullanıcı: {current_user}")
    print(f"Veritabanı: {current_database}")