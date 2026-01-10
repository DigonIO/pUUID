"""
pUUID - Prefixed UUIDs for Python with Pydantic & SQLAlchemy support.

Author: Jendrik Potyka, Fabian Preiss
"""

__version__ = "1.1.0"
__author__ = "Jendrik Potyka, Fabian Preiss"


from puuid.base import (
    PUUIDBase,
    PUUIDError,
    PUUIDv1,
    PUUIDv3,
    PUUIDv4,
    PUUIDv5,
    PUUIDv6,
    PUUIDv7,
    PUUIDv8,
)

PUUID = PUUIDBase  # backwards compatibility

__all__ = [
    "PUUID",
    "PUUIDBase",
    "PUUIDv1",
    "PUUIDv3",
    "PUUIDv4",
    "PUUIDv5",
    "PUUIDv6",
    "PUUIDv7",
    "PUUIDv8",
    "PUUIDError",
]
