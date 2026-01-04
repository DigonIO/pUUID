"""
pUUID - Prefixed UUID's for Python with Pydantic & SQLAlchemy support.

Author: Jendrik Potyka, Fabian Preiss
"""

__version__ = "1.0.0"
__author__ = "Jendrik Potyka, Fabian Preiss"


from puuid.base import PUUID, PUUIDError
from puuid.sqlalchemy import SqlPUUID

__all__ = [
    "PUUID",
    "PUUIDError",
    "SqlPUUID",
]
