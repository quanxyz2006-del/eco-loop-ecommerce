"""Create or promote an administrator account from the local terminal."""

import argparse
from getpass import getpass

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import User, UserRole
from app.services.initialization import initialise_database


def main() -> None:
    parser = argparse.ArgumentParser(description="Tạo tài khoản quản trị ECO-LOOP")
    parser.add_argument("--email", required=True, help="Email đăng nhập quản trị")
    parser.add_argument("--name", default="Quản trị ECO-LOOP", help="Tên hiển thị")
    args = parser.parse_args()
    password = getpass("Mật khẩu (tối thiểu 8 ký tự): ")
    confirmation = getpass("Nhập lại mật khẩu: ")
    if password != confirmation:
        parser.error("Hai mật khẩu không khớp.")
    if len(password) < 8 or len(password.encode("utf-8")) > 72:
        parser.error("Mật khẩu cần từ 8 ký tự và không quá 72 byte.")
    initialise_database()
    with SessionLocal() as db:
        email = args.email.strip().lower()
        user = db.scalar(select(User).where(func.lower(User.email) == email))
        if user is None:
            user = User(full_name=args.name.strip(), email=email, password_hash=hash_password(password))
            db.add(user)
        else:
            user.full_name = args.name.strip()
            user.password_hash = hash_password(password)
        user.role = UserRole.ADMIN
        db.commit()
    print(f"Đã sẵn sàng tài khoản quản trị: {email}")


if __name__ == "__main__":
    main()
