#!/usr/bin/env python3
from pathlib import Path

import jwt


def make(name: str, key: bytes):
    return jwt.encode(
        {"system": "dev", "system_identifier": name}, key, algorithm="RS256"
    )


if __name__ == "__main__":
    import cryptography

    with Path("dev_fixtures/priv").open() as f:
        key = f.read().encode("utf8")
    key = cryptography.hazmat.primitives.serialization.load_ssh_private_key(key, b"")
    print(make("tom", key))
