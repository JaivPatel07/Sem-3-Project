import argparse
import os
from pathlib import Path

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv


def load_environment(project_dir: Path) -> None:
    env_example = project_dir / '.env.example'
    env_file = project_dir / '.env'

    if env_example.exists():
        load_dotenv(env_example)
    if env_file.exists():
        load_dotenv(env_file, override=True)


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f'Missing required environment variable: {name}')
    return value


def create_database_if_missing(host: str, port: str, user: str, password: str, db_name: str) -> bool:
    created = False
    connection = psycopg2.connect(host=host, port=port, user=user, password=password, dbname='postgres')
    connection.autocommit = True
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1 FROM pg_database WHERE datname=%s', (db_name,))
            if cursor.fetchone() is None:
                cursor.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(db_name)))
                created = True
    finally:
        connection.close()
    return created


def apply_schema(host: str, port: str, user: str, password: str, db_name: str, schema_path: Path) -> None:
    if not schema_path.exists():
        raise FileNotFoundError(f'Schema file not found: {schema_path}')

    schema_sql = schema_path.read_text(encoding='utf-8')

    connection = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=db_name)
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(schema_sql)
    finally:
        connection.close()


def list_tables(host: str, port: str, user: str, password: str, db_name: str) -> list[str]:
    connection = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=db_name)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
            return [row[0] for row in cursor.fetchall()]
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description='Initialize PostgreSQL database and apply schema.')
    parser.add_argument(
        '--schema',
        default='schema_v2.sql',
        help='Schema file path relative to project root (default: schema_v2.sql)',
    )
    args = parser.parse_args()

    project_dir = Path(__file__).resolve().parent
    load_environment(project_dir)

    host = require_env('DB_HOST')
    port = require_env('DB_PORT')
    user = require_env('DB_USER')
    password = require_env('DB_PASSWORD')
    db_name = require_env('DB_NAME')

    schema_path = (project_dir / args.schema).resolve()

    created = create_database_if_missing(host, port, user, password, db_name)
    if created:
        print(f'Created database: {db_name}')
    else:
        print(f'Database already exists: {db_name}')

    apply_schema(host, port, user, password, db_name, schema_path)
    print(f'Applied schema: {schema_path}')

    tables = list_tables(host, port, user, password, db_name)
    if tables:
        print('Tables:', ', '.join(tables))
    else:
        print('No tables found in public schema.')


if __name__ == '__main__':
    main()
