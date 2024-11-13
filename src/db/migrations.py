import logging
from src.db.pool import get_db_pool
from packaging import version as packaging_version
from src.lang.director import humanize
from src.lang.decorators import with_locale

MIGRATIONS = [
    {
        "bot_version": "0.6.3",
        "up": [
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                version TEXT PRIMARY KEY
            )
            """,
            "INSERT OR IGNORE INTO schema_version (version) VALUES ('0.6.3')",
        ],
        "down": [
            "DROP TABLE IF EXISTS schema_version",
        ]
    },
    {
        "bot_version": "0.6.4",
        "up": [
            """
            CREATE TABLE IF NOT EXISTS users_new (
                telegram_id BIGINT PRIMARY KEY,
                first_access_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_access_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_admin BOOLEAN DEFAULT FALSE,
                is_banned BOOLEAN DEFAULT FALSE,
                is_deleted BOOLEAN DEFAULT FALSE,
                lang TEXT DEFAULT 'en'
            )
            """,
            "INSERT INTO users_new SELECT telegram_id, first_access_date, last_access_date, is_admin, is_banned, is_deleted, 'en' FROM users",
            "DROP TABLE users",
            "ALTER TABLE users_new RENAME TO users"
        ],
        "down": [
            "ALTER TABLE users DROP COLUMN lang"
        ]
    },
    {
        "bot_version": "0.6.6",
        "up": [
            """
            CREATE TABLE IF NOT EXISTS active_tasks (
                telegram_id BIGINT,
                uuid TEXT PRIMARY KEY,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
            )
            """
        ],
        "down": [
            "DROP TABLE IF EXISTS active_tasks"
        ]
    },
    {
        "bot_version": "0.7.0",
        "up": [
            """
            CREATE TABLE IF NOT EXISTS users_new (
                telegram_id BIGINT PRIMARY KEY,
                first_access_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_access_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_admin BOOLEAN DEFAULT FALSE,
                is_banned BOOLEAN DEFAULT FALSE,
                is_deleted BOOLEAN DEFAULT FALSE,
                lang TEXT DEFAULT 'en',
                api_requests_count INTEGER DEFAULT 0
            )
            """,
            """
            INSERT INTO users_new 
            SELECT 
                telegram_id, 
                first_access_date, 
                last_access_date, 
                is_admin, 
                is_banned, 
                is_deleted, 
                lang,
                0 
            FROM users
            """,
            "DROP TABLE users",
            "ALTER TABLE users_new RENAME TO users"
        ],
        "down": [
            """
            CREATE TABLE users_old AS 
            SELECT 
                telegram_id, 
                first_access_date, 
                last_access_date, 
                is_admin, 
                is_banned, 
                is_deleted,
                lang
            FROM users
            """,
            "DROP TABLE users",
            "ALTER TABLE users_old RENAME TO users"
        ]
    },
    {
        "bot_version": "0.7.2",
        "up": [
            """
            CREATE TABLE users_new (
                telegram_id BIGINT PRIMARY KEY,
                first_access_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_access_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_admin BOOLEAN DEFAULT FALSE,
                is_banned BOOLEAN DEFAULT FALSE,
                is_deleted BOOLEAN DEFAULT FALSE,
                api_requests_count INTEGER DEFAULT 0
            )
            """,
            """
            INSERT INTO users_new 
            SELECT 
                telegram_id, 
                first_access_date, 
                last_access_date, 
                is_admin, 
                is_banned, 
                is_deleted,
                api_requests_count
            FROM users
            """,
            "DROP TABLE users",
            "ALTER TABLE users_new RENAME TO users"
        ],
        "down": [
            """
            ALTER TABLE users ADD COLUMN lang TEXT DEFAULT 'en'
            """
        ]
    }
]

@with_locale
async def get_current_version() -> str:
    try:
        db = await get_db_pool()
        async with db.execute('SELECT version FROM schema_version') as cursor:
            result = await cursor.fetchone()
            return result[0] if result else '0.0.0'
    except Exception as e:
        logging.error(await humanize("DATABASE_VERSION_ERROR").format(error=str(e)))
        raise

async def set_version(version: str) -> None:
    try:
        db = await get_db_pool()
        async with db.cursor() as cursor:
            await cursor.execute('DELETE FROM schema_version')
            await cursor.execute('INSERT INTO schema_version (version) VALUES (?)', (version,))
        await db.commit()
        logging.info(f"Database version updated to {version}")
    except Exception as e:
        logging.error(f"Error setting database version: {e}")
        raise

async def apply_migration(migration: dict) -> None:
    db = await get_db_pool()
    try:
        for query in migration["up"]:
            await db.execute(query)
        await db.commit()
        logging.info(f"Applied migration to version {migration['bot_version']}")
    except Exception as e:
        logging.error(f"Error applying migration {migration['bot_version']}: {e}")
        raise

def version_greater(version1: str, version2: str) -> bool:
    return packaging_version.parse(version1) > packaging_version.parse(version2)

@with_locale
async def check_and_fix_table_structure() -> None:
    db = await get_db_pool()
    try:
        async with db.execute("PRAGMA table_info(users)") as cursor:
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]

        if 'api_requests_count' not in column_names:
            logging.info("Adding missing column api_requests_count to users table")
            await db.execute('''
                CREATE TABLE users_new (
                    telegram_id BIGINT PRIMARY KEY,
                    first_access_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_access_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_admin BOOLEAN DEFAULT FALSE,
                    is_banned BOOLEAN DEFAULT FALSE,
                    is_deleted BOOLEAN DEFAULT FALSE,
                    lang TEXT DEFAULT 'en',
                    api_requests_count INTEGER DEFAULT 0
                )
            ''')
            
            await db.execute('''
                INSERT INTO users_new 
                SELECT 
                    telegram_id, 
                    first_access_date, 
                    last_access_date, 
                    is_admin, 
                    is_banned, 
                    is_deleted,
                    lang,
                    0 
                FROM users
            ''')
            
            await db.execute("DROP TABLE users")
            await db.execute("ALTER TABLE users_new RENAME TO users")
            await db.commit()
            logging.info("Successfully added api_requests_count column")

    except Exception as e:
        logging.error(await humanize("DATABASE_MIGRATION_ERROR").format(error=str(e)))
        raise

@with_locale
async def run_migrations(current_bot_version: str) -> None:
    try:
        await check_and_fix_table_structure()
        
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

        if version_greater(current_bot_version, current_db_version):
            await set_version(current_bot_version)
            logging.info(f"Updated database version to current bot version: {current_bot_version}")

        if applied_migrations > 0:
            logging.info(f"Applied {applied_migrations} migrations. Database is now at version {current_bot_version}")
        else:
            logging.info("No migrations were necessary. Database is up to date.")
    except Exception as e:
        logging.error(await humanize("DATABASE_MIGRATION_ERROR").format(error=str(e)))
        raise
