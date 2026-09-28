import hashlib
import os
import hmac

def get_password_hash(password: str) -> str:
    salt = os.urandom(16).hex()
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 100000).hex()
    return f"pbkdf2_sha256:{salt}:{key}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        if hashed_password.startswith("pbkdf2_sha256:"):
            parts = hashed_password.split(":")
            if len(parts) == 3:
                salt, key = parts[1], parts[2]
                test_key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), bytes.fromhex(salt), 100000).hex()
                return hmac.compare_digest(key, test_key)
        return plain_password == hashed_password
    except Exception:
        return plain_password == hashed_password
