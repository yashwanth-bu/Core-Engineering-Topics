from passlib.context import CryptContext
import hashlib

# ================================================================
# SHARED bcrypt configuration
# ================================================================
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# ================================================================
# VERSION 1 (NOT RECOMMENDED)
# SHA-256  ➜  bcrypt (double hashing)
# ================================================================
# This version FIRST hashes the password using SHA-256,
# then hashes the SHA-256 output using bcrypt.
#
# This is often done by beginners thinking:
# "More hashing = more security"
#
# In reality:
# - SHA-256 is very fast → bad for passwords
# - bcrypt already does salting + slow hashing
# - This adds complexity without improving security
# ================================================================

def hash_password_sha_then_bcrypt(password: str) -> str:
    """
    1. Convert password to bytes
    2. Hash it with SHA-256 (fast hash)
    3. Pass the SHA-256 result into bcrypt
    """
    sha256_hash = hashlib.sha256(password.encode()).digest()
    return pwd_context.hash(sha256_hash)


def verify_password_sha_then_bcrypt(password: str, hashed_password: str) -> bool:
    """
    To verify:
    - Hash the input password again using SHA-256
    - Compare it with the stored bcrypt hash
    """
    sha256_hash = hashlib.sha256(password.encode()).digest()
    return pwd_context.verify(sha256_hash, hashed_password)


# ================================================================
# VERSION 2 (RECOMMENDED)
# bcrypt ONLY
# ================================================================
# This is the correct and modern approach.
#
# bcrypt:
# - Generates a random salt automatically
# - Uses a slow, adaptive algorithm
# - Stores everything needed for verification
# ================================================================

def hash_password_bcrypt_only(password: str) -> str:
    """
    Hash a plain-text password directly with bcrypt.
    No manual hashing required.
    """
    return pwd_context.hash(password)


def verify_password_bcrypt_only(password: str, hashed_password: str) -> bool:
    """
    Verify a password using bcrypt only.
    """
    return pwd_context.verify(password, hashed_password)


# ================================================================
# DEMO / COMPARISON
# ================================================================
if __name__ == "__main__":

    user_password = "user"

    print("=== VERSION 1: SHA-256 ➜ bcrypt (NOT RECOMMENDED) ===")
    hash_v1 = hash_password_sha_then_bcrypt(user_password)
    print("Stored hash:", hash_v1)
    print("Valid password:", verify_password_sha_then_bcrypt("user", hash_v1))
    print("Wrong password:", verify_password_sha_then_bcrypt("wrong", hash_v1))

    print("\n=== VERSION 2: bcrypt ONLY (RECOMMENDED) ===")
    hash_v2 = hash_password_bcrypt_only(user_password)
    print("Stored hash:", hash_v2)
    print("Valid password:", verify_password_bcrypt_only("user", hash_v2))
    print("Wrong password:", verify_password_bcrypt_only("wrong", hash_v2))
