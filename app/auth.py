import hashlib
import os
from functools import wraps

from configs.config import CONFIG_PATH
from flask import jsonify, session

MASTER_KEY_HASH_PATH = CONFIG_PATH.parent / "master_key.hash"


def is_master_key_initialized():
    return MASTER_KEY_HASH_PATH.exists()


def initialize_master_key(master_key):
    """Set up the master key for the first time"""
    if MASTER_KEY_HASH_PATH.exists():
        raise RuntimeError("Master key already initialized")

    # Create pepper (additional secret)
    pepper = os.urandom(16)
    with open(CONFIG_PATH.parent / "pepper.bin", "wb") as f:
        f.write(pepper)

    # Hash the master key with pepper
    hashed = hashlib.pbkdf2_hmac("sha256", master_key.encode(), pepper, 100000)

    with open(MASTER_KEY_HASH_PATH, "wb") as f:
        f.write(hashed)


def verify_master_key(master_key):
    """Verify the master key"""
    if not MASTER_KEY_HASH_PATH.exists():
        return True  # First time setup

    with open(CONFIG_PATH.parent / "pepper.bin", "rb") as f:
        pepper = f.read()

    with open(MASTER_KEY_HASH_PATH, "rb") as f:
        stored_hash = f.read()

    new_hash = hashlib.pbkdf2_hmac("sha256", master_key.encode(), pepper, 100000)

    return new_hash == stored_hash


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "master_key" not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)

    return decorated_function
