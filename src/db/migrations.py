import logging
from src.db.common import get_db_pool
from packaging import version as packaging_version

# Список миграций. Каждая миграция - это словарь с версией бота и SQL-запросами
MIGRATIONS = [
    {
        "bot_version": "0.6.3",
        "up": [
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                version TEXT PRIMARY KEY
            )
            """,
            "INSERT INTO schema_version (version) VALUES ('0.6.3')",
        ],
        "down": [
            "DROP TABLE IF EXISTS schema_version",
        ]
    },
    {
        "bot_version": "0.6.4",
        "up": [
            "ALTER TABLE users ADD COLUMN lang TEXT DEFAULT 'en'",
        ],
        "down": [
            "ALTER TABLE users DROP COLUMN lang",
        ]
    },
    # Добавляйте новые миграции сюда
]

async def get_current_version():
    db = await get_db_pool()
    try:
        async with db.execute("SELECT version FROM schema_version") as cursor:
            result = await cursor.fetchone()
            return result[0] if result else "0.0.0"
    except Exception:
        return "0.0.0"

async def set_version(version):
    db = await get_db_pool()
    await db.execute("UPDATE schema_version SET version = ?", (version,))
    await db.commit()

async def apply_migration(migration):
    db = await get_db_pool()
    for query in migration["up"]:
        await db.execute(query)
    await db.commit()
    logging.info(f"Applied migration to version {migration['bot_version']}")

def version_greater(v1, v2):
    return packaging_version.parse(v1) > packaging_version.parse(v2)

async def run_migrations(current_bot_version):
    current_db_version = await get_current_version()
    logging.info(f"Current database version: {current_db_version}")
    logging.info(f"Current bot version: {current_bot_version}")

    applied_migrations = 0
    for migration in sorted(MIGRATIONS, key=lambda m: packaging_version.parse(m["bot_version"])):
        if version_greater(migration["bot_version"], current_db_version) and not version_greater(migration["bot_version"], current_bot_version):
            logging.info(f"Applying migration to version {migration['bot_version']}")
            await apply_migration(migration)
            await set_version(migration["bot_version"])
            applied_migrations += 1

    if applied_migrations > 0:
        logging.info(f"Applied {applied_migrations} migrations. Database is now at version {current_bot_version}")
    else:
        logging.info("No migrations were necessary. Database is up to date.")
