"""
VEINHasher: Secure, deterministic hashing of EINs using bucketed HKDF-derived HMAC

Key Features:
- One main key, derived via HKDF per bucket
- Secret modulus to determine bucket assignment
- Validates EINs (accepts dashes, requires 9 digits)

It reads configuration from two separate .env files:
- `.env.main_key` should contain `MAIN_KEY=<hex string>`
- `.env.main_modulus` should contain `MAIN_MODULUS=<integer>`
- On first run, generates `.env.main_key` if missing

EINs can be provided in formats with dashes (e.g., 12-3456789 or 123-45-6789),
but any other non-numeric characters will raise an error.

This design offers a balanced mix of security, performance, and operational simplicity,
making it ideal for stable hashing of low-entropy identifiers like EINs—especially when
you want to guard against enumeration and futureproof for scale or regulation.

Why this design makes sense:

1. Strong Security with Minimal Overhead:
   HKDF generates cryptographically strong, deterministic salts per bucket from one main key—no need to store thousands of keys.
   A random modulus obscures the bucket assignment logic, making reverse engineering harder.

2. Scalability without Complexity:
   Easily supports millions of EINs without requiring massive storage or key management infrastructure.
   Stateless derivation = no key database required.

3. Defense in Depth:
   Even if the main key leaks, an attacker still needs to guess the modulus to reconstruct bucket mappings.
   Even if the modulus leaks, brute-forcing without the main key remains computationally hard.

4. Future-Proofing:
   You can scale up by increasing the modulus or changing the HKDF info string (e.g., add a version tag).
   Supports key rotation and versioning without architectural change.

"""

import os
import hmac
import hashlib
import secrets
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

class VEINHasher:
    @staticmethod
    def _load_env_file(filepath: str) -> dict:
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"Required config file '{filepath}' not found.")
        env_vars = {}
        with open(filepath, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    env_vars[key.strip()] = value.strip()
        return env_vars

    @staticmethod
    def _generate_main_key_file(filepath: str) -> bytes:
        """
        Generate a new secure main key and write it to the given .env file.
        """
        key = secrets.token_hex(32)  # 256-bit key = 64 hex characters
        with open(filepath, 'w') as f:
            f.write(f"MAIN_KEY={key}\n")
        print(f"Generated new MAIN_KEY and saved to {filepath}")
        return bytes.fromhex(key)

    @staticmethod
    def _load_main_key() -> bytes:
        path = '.env.main_key'
        if not os.path.isfile(path):
            return VEINHasher._generate_main_key_file(path)

        env = VEINHasher._load_env_file(path)
        if 'MAIN_KEY' not in env:
            raise EnvironmentError("MAIN_KEY not found in .env.main_key")
        key_hex = env['MAIN_KEY']
        if len(key_hex) < 64:
            raise ValueError("MAIN_KEY must be at least 64 hex characters (256 bits)")
        try:
            return bytes.fromhex(key_hex)
        except ValueError:
            raise ValueError("MAIN_KEY must be a valid hex string")

    @staticmethod
    def _load_modulus() -> int:
        env = VEINHasher._load_env_file('.env.main_modulus')
        if 'MAIN_MODULUS' not in env:
            raise EnvironmentError("MAIN_MODULUS not found in .env.main_modulus")
        try:
            return int(env['MAIN_MODULUS'])
        except ValueError:
            raise ValueError("MAIN_MODULUS must be an integer")

    @staticmethod
    def _normalize_ein(ein: str) -> str:
        ein = ein.strip().replace('-', '')
        if not ein.isdigit():
            raise ValueError("EIN/TIN must contain only digits and optional dashes")
        if len(ein) != 9:
            raise ValueError("EIN/TIN must be exactly 9 digits after normalization")
        return ein

    @staticmethod
    def _derive_salt(main_key: bytes, bucket_id: int) -> bytes:
        info = f"bucket-{bucket_id}".encode()
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=info,
            backend=default_backend()
        )
        return hkdf.derive(main_key)

    @staticmethod
    def hash(ein: str) -> str:
        ein = VEINHasher._normalize_ein(ein)
        main_key = VEINHasher._load_main_key()
        modulus = VEINHasher._load_modulus()
        bucket_id = int(ein) % modulus
        salt = VEINHasher._derive_salt(main_key, bucket_id)
        h = hmac.new(salt, ein.encode(), hashlib.sha256)
        return h.hexdigest()
