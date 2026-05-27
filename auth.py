"""Flask-Login user model and helpers."""

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

import database


class User(UserMixin):
    def __init__(self, user_id: int, username: str):
        self.id = user_id
        self.username = username


def load_user(user_id: str):
    row = database.get_user_by_id(int(user_id))
    if row is None:
        return None
    return User(row["id"], row["username"])


def register_user(username: str, password: str) -> User:
    username = username.strip()
    if not username or not password:
        raise ValueError("Username and password are required.")
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters.")

    if database.get_user_by_username(username):
        raise ValueError("Username already taken.")

    password_hash = generate_password_hash(password, method="pbkdf2:sha256")
    user_id = database.create_user(username, password_hash)
    return User(user_id, username)


def authenticate_user(username: str, password: str):
    row = database.get_user_by_username(username.strip())
    if row is None or not check_password_hash(row["password_hash"], password):
        return None
    return User(row["id"], row["username"])
