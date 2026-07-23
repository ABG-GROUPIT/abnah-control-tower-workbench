from __future__ import annotations

from sqlalchemy import text

from loaders.db import get_engine


def main() -> None:
    engine = get_engine()
    with engine.connect() as conn:
        schemas = [
            row[0]
            for row in conn.execute(
                text(
                    """
                    SELECT schema_name
                    FROM information_schema.schemata
                    WHERE schema_name IN ('raw', 'control', 'analytics', 'staging')
                    ORDER BY schema_name
                    """
                )
            )
        ]
        raw_tables = [
            row[0]
            for row in conn.execute(
                text(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'raw'
                      AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                    """
                )
            )
        ]
        analytics_views = [
            row[0]
            for row in conn.execute(
                text(
                    """
                    SELECT table_name
                    FROM information_schema.views
                    WHERE table_schema = 'analytics'
                    ORDER BY table_name
                    """
                )
            )
        ]
        analytics_tables = [
            row[0]
            for row in conn.execute(
                text(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'analytics'
                    ORDER BY table_name
                    """
                )
            )
        ]

    print(f"schemas={schemas}")
    print(f"raw_tables={raw_tables}")
    print(f"analytics_tables={analytics_tables}")
    print(f"analytics_views={analytics_views}")


if __name__ == "__main__":
    main()

