"""Create an online SQLite backup or copy its rows into an empty MySQL database."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

BACKEND_PATH = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))


def create_backup(source_path: Path, destination_path: Path) -> None:
    """Use SQLite's online backup API so an active local database is not copied raw."""
    source_path = source_path.resolve()
    destination_path = destination_path.resolve()
    required_root = Path("D:/CodexData/eco-loop/migration").resolve()
    if required_root not in destination_path.parents:
        raise SystemExit("Bản sao lưu phải nằm dưới D:/CodexData/eco-loop/migration.")
    if not source_path.is_file():
        raise SystemExit(f"Không tìm thấy SQLite nguồn: {source_path}")
    if destination_path.exists():
        raise SystemExit(f"Từ chối ghi đè bản sao lưu đã có: {destination_path}")

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(source_path) as source, sqlite3.connect(destination_path) as backup:
        source.backup(backup)
        integrity = backup.execute("PRAGMA integrity_check").fetchone()
        if not integrity or integrity[0] != "ok":
            raise RuntimeError("Kiểm tra toàn vẹn bản sao lưu SQLite thất bại.")
        tables = backup.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        counts = {
            name: backup.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
            for (name,) in tables
        }
    print(f"SQLite backup verified; tables={len(counts)}; destination={destination_path}")
    for table_name, row_count in sorted(counts.items()):
        print(f"{table_name}: {row_count}")


def migrate_backup(source_path: Path) -> None:
    """Copy modeled rows in FK order into a newly initialized, empty MySQL schema."""
    from sqlalchemy import create_engine, func, inspect, select

    from app.core.config import settings
    from app.core.database import Base
    import app.models  # Register every mapped table on Base.metadata.

    source_path = source_path.resolve()
    if not source_path.is_file():
        raise SystemExit(f"Không tìm thấy bản sao lưu SQLite trong container: {source_path}")
    if not settings.database_url.startswith(("mysql+", "mariadb+")):
        raise SystemExit("DATABASE_URL đích phải trỏ tới MySQL/MariaDB.")

    source_engine = create_engine(f"sqlite:///{source_path.as_posix()}")
    target_engine = create_engine(settings.database_url, pool_pre_ping=True)
    try:
        if not Base.metadata.tables:
            raise RuntimeError("Không có model nào được đăng ký để chuyển dữ liệu.")
        source_inspector = inspect(source_engine)
        Base.metadata.create_all(target_engine)
        target_inspector = inspect(target_engine)
        target_tables = set(target_inspector.get_table_names())

        with target_engine.connect() as target_connection:
            for table in Base.metadata.sorted_tables:
                if table.name not in target_tables:
                    continue
                if target_connection.execute(select(table).limit(1)).first() is not None:
                    raise SystemExit(
                        f"Bảng đích {table.name!r} đã có dữ liệu; dừng để tránh ghi đè."
                    )

        source_tables = set(source_inspector.get_table_names())
        copied: dict[str, int] = {}
        with source_engine.connect() as source_connection, target_engine.begin() as target_connection:
            for table in Base.metadata.sorted_tables:
                if table.name not in source_tables or table.name not in target_tables:
                    continue
                rows = [dict(row) for row in source_connection.execute(select(table)).mappings()]
                # The category hierarchy is shallow; insert roots before their children.
                if table.name == "categories" and "parent_id" in table.c:
                    rows.sort(key=lambda row: row.get("parent_id") is not None)
                if rows:
                    target_connection.execute(table.insert(), rows)
                copied[table.name] = len(rows)

        with target_engine.connect() as target_connection:
            for table_name, expected_count in copied.items():
                table = Base.metadata.tables[table_name]
                actual_count = target_connection.execute(
                    select(func.count()).select_from(table)
                ).all()
                if actual_count[0][0] != expected_count:
                    raise RuntimeError(
                        f"Đối soát bảng {table_name!r} không khớp sau khi chuyển dữ liệu."
                    )
    finally:
        source_engine.dispose()
        target_engine.dispose()

    if not copied:
        raise RuntimeError("Không có bảng dữ liệu nào được chuyển từ SQLite.")
    print(f"SQLite-to-MySQL migration verified; tables={len(copied)}")
    for table_name, row_count in sorted(copied.items()):
        print(f"{table_name}: {row_count}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backup-only", action="store_true")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path)
    args = parser.parse_args()

    if args.backup_only:
        if args.destination is None:
            parser.error("--destination là bắt buộc với --backup-only")
        create_backup(args.source, args.destination)
    else:
        migrate_backup(args.source)


if __name__ == "__main__":
    main()
