from psycopg2.pool import ThreadedConnectionPool

from shared.utility import load_from_json

CONFIG_FILE = "config/config.json"

def create_connection_pool() -> ThreadedConnectionPool:
    """Create and return a PostgreSQL connection"""
    config = load_from_json(CONFIG_FILE, "postgres")

    return ThreadedConnectionPool(
        minconn=1,
        maxconn=5,
        host=config["DB_HOST"],
        port=config["DB_PORT"],
        dbname=config["DB_NAME"],
        user=config["DB_USER"],
        password=config["DB_PASSWORD"],
    )