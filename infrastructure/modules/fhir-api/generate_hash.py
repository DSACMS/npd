#!/usr/bin/env python

import base64
import hashlib
import json
import secrets
import sys


def hash_password(
    password, salt=None, iterations=1000000
):  # Default iterations for current Django versions
    if salt is None:
        salt = secrets.token_hex(16)
    assert salt and isinstance(salt, str) and "$" not in salt
    assert isinstance(password, str)
    pw_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
    )
    b64_hash = base64.b64encode(pw_hash).decode("ascii").strip()
    return "{}${}${}${}".format("pbkdf2_sha256", iterations, salt, b64_hash)


if __name__ == "__main__":
    query = json.loads(sys.stdin.read())
    password = query["password_input"]
    if not password:
        sys.exit(1)
    hashed_password = hash_password(password)
    print(json.dumps({"hashed_password": hashed_password}))
