# pUUID

**pUUID** - Prefixed UUID's for Python with **Pydantic** & **SQLAlchemy** support

[![repository](https://img.shields.io/badge/src-GitLab-orange)](https://gitlab.com/DigonIO/pypermission)
[![mirror](https://img.shields.io/badge/mirror-GitHub-orange)](https://github.com/DigonIO/pypermission)
[![License: LGPLv3](https://gitlab.com/DigonIO/pypermission/-/raw/main/assets/badges/license.svg)](https://spdx.org/licenses/LGPL-3.0-only.html)
[![pipeline status](https://gitlab.com/DigonIO/pypermission/badges/main/pipeline.svg)](https://gitlab.com/DigonIO/pypermission/-/pipelines)
[![coverage report](https://gitlab.com/DigonIO/pypermission/badges/main/coverage.svg)](https://gitlab.com/DigonIO/pypermission/-/pipelines)
[![Code style: black](https://gitlab.com/DigonIO/pypermission/-/raw/main/assets/badges/black.svg)](https://github.com/psf/black)
[![Imports: isort](https://gitlab.com/DigonIO/pypermission/-/raw/main/assets/badges/isort.svg)](https://pycqa.github.io/isort/)

[![pkgversion](https://img.shields.io/pypi/v/pypermission)](https://pypi.org/project/pypermission/)
[![versionsupport](https://img.shields.io/pypi/pyversions/pypermission)](https://pypi.org/project/pypermission/)
[![Downloads Week](https://pepy.tech/badge/pypermission/week)](https://pepy.tech/project/pypermission)
[![Downloads Total](https://pepy.tech/badge/pypermission)](https://pepy.tech/project/pypermission)

## Features

- Prefixed UUIDv4's for Python
- Variable prefix length
- Supports **Pydantic**
- Supports **SQLAlchemy**
- Typing!

## When should I use pUUID?

Use **pUUID** when a plain UUIDs just isn’t expressive enough.

If this...

```
b100f10f-6876-4b61-984f-2c74be42fcd4
```

...makes you ask "UUID of what, exactly?", and this...

```
user_b100f10f-6876-4b61-984f-2c74be42fcd4
```

...makes you instantly happier, then **pUUID** is for you.

It’s especially useful when:

- You use FastAPI or some kind of Pydantic API
- Your database layer uses SQLAlchemy
- You want type safety and human-readable IDs
- You’ve ever mixed up an _user_id_ with a _group_id_

## Installing **pUUID** with pip

The **pUUID** library can be installed directly from the PyPI repositories with:

```console
pip install pUUID
```

If you want to use the **SQLAlchemy** feature, you need to install the `sqlalchemy` dependency group:

```console
pip install 'pUUID[sqlalchemy]'
```

## Basic Usage

```py
from typing import Literal
from uuid import UUID
from puuid import PUUID


class UserUUID(PUUID[Literal["user"]]):
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

```py
from pydantic import BaseModel

class User(BaseModel):
    user_id: UserUUID

user = User(user_id=UserUUID())
```

## SQLALchemy Usage

```py
from sqlalchemy.orm import DeclarativeBase
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

## License

- **Library source code:** Licensed under [LGPLv3](https://spdx.org/licenses/LGPL-3.0-only.html).
