import hmac
import os
import hashlib


def generate_salt():
    return os.urandom(16)


def hash_password(password, salt):
    hashed_password = hashlib.pbkdf2_hmac(
        'sha256',  # Hash algorithm
        password.encode('utf-8'),  # Password in bytes
        salt,  # Salt in bytes
        100000  # Number of iterations (higher is more secure but slower)
    )
    return hashed_password.hex()  # Return as a hexadecimal string


def verify_password(stored_password_hash, stored_salt, provided_password):
    # Use the same hashing method as during creation
    rehashed_password = hashlib.pbkdf2_hmac(
        'sha256',
        provided_password.encode('utf-8'),
        stored_salt,
        100000
    ).hex()
    return hmac.compare_digest(rehashed_password, stored_password_hash)


salt = generate_salt()
password = "cameron7"
hashed_pw = hash_password(password, salt)

print(f"Generated Salt: {salt.hex()}")
print(f"Hashed Password: {hashed_pw}")

# Verification
is_correct = verify_password(hashed_pw, salt, "cameron7")
print(f"Password verification successful: {is_correct}")

is_incorrect = verify_password(hashed_pw, salt, "wrongpassword")
print(f"Wrong password verification successful: {is_incorrect}")