---
description: "pUUID - Prefixed UUIDs for Python with Pydantic & SQLAlchemy support."
---

# pUUID - Quick Start

The **pUUID** library can be installed directly from the [PyPI repositories](https://pypi.org/project/PyPermission/) with:

```bash
pip install pUUID
```

If you want to use the **SQLAlchemy** feature, you need to install the `sqlalchemy` dependency group:

```bash
pip install 'pUUID[sqlalchemy]'
```

## Basic Usage

```python
from typing import Literal
from uuid import UUID
from puuid import PUUIDv4


class UserUUID(PUUIDv4[Literal["user"]]):
    _prefix = "user"

# Create a random PUUID
user_id = UserUUID()

# Create a PUUID with a specific UUID
user_id = UserUUID(UUID('b100f10f-6876-4b61-984f-2c74be42fcd4'))

# Serialize a PUUID:
serial_puuid = user_id.to_string()

# Deserialize a PUUID
user_id = UserUUID.from_string(serial_puuid)
```

## Pydantic Usage

```{.python continuation}
from pydantic import BaseModel

class User(BaseModel):
    user_id: UserUUID

user = User(user_id=UserUUID())
```

## SQLALchemy Usage

```{.python continuation}
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from puuid.sqlalchemy import SqlPUUID


class BaseORM(DeclarativeBase): ...

class UserORM(BaseORM):
    __tablename__ = "user_table"

    id: Mapped[UserUUID] = mapped_column(
        SqlPUUID(UserUUID, prefix_length=4),
        primary_key=True,
        default=UserUUID.factory,
    )
```
