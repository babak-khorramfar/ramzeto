import os
import hashlib

HASH_FILE = os.path.join("data", "master.hash")


def hash_password(password: str) -> str:
    """هش‌کردن رمز با SHA-256"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def master_exists() -> bool:
    """بررسی وجود فایل رمز اصلی"""
    return os.path.exists(HASH_FILE)


def save_master_password(password: str):
    """ذخیره هش رمز اصلی"""
    hashed = hash_password(password)
    with open(HASH_FILE, "w") as f:
        f.write(hashed)


def check_master_password(password: str) -> bool:
    """مقایسه رمز واردشده با هش ذخیره‌شده"""
    if not master_exists():
        return False
    with open(HASH_FILE, "r") as f:
        stored_hash = f.read().strip()
    return stored_hash == hash_password(password)


_current_password = None


def clear_current_password():
    global _current_password
    _current_password = None


def set_current_password(pwd: str):
    global _current_password
    _current_password = pwd


def get_current_password() -> str:
    return _current_password
