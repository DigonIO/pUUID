# pUUID

**pUUID** - Prefixed UUIDs for Python with **Pydantic** & **SQLAlchemy** support.

[![repository](https://img.shields.io/badge/src-GitLab-orange)](https://gitlab.com/DigonIO/puuid)
[![mirror](https://img.shields.io/badge/mirror-GitHub-orange)](https://github.com/DigonIO/puuid)
[![License: LGPLv3](https://gitlab.com/DigonIO/puuid/-/raw/main/assets/badges/license.svg)](https://spdx.org/licenses/LGPL-3.0-only.html)
[![pipeline status](https://gitlab.com/DigonIO/puuid/badges/main/pipeline.svg)](https://gitlab.com/DigonIO/puuid/-/pipelines)
[![coverage report](https://gitlab.com/DigonIO/puuid/badges/main/coverage.svg)](https://gitlab.com/DigonIO/puuid/-/pipelines)
[![Code style: black](https://gitlab.com/DigonIO/puuid/-/raw/main/assets/badges/black.svg)](https://github.com/psf/black)
[![Imports: isort](https://gitlab.com/DigonIO/puuid/-/raw/main/assets/badges/isort.svg)](https://pycqa.github.io/isort/)

[![pkgversion](https://img.shields.io/pypi/v/puuid)](https://pypi.org/project/puuid/)
[![versionsupport](https://img.shields.io/pypi/pyversions/puuid)](https://pypi.org/project/puuid/)
[![Downloads Week](https://pepy.tech/badge/puuid/week)](https://pepy.tech/project/puuid)
[![Downloads Total](https://pepy.tech/badge/puuid)](https://pepy.tech/project/puuid)

## Features

- **Human-Friendly UUIDs:** `user_019b956e...` instead of just  `019b956e...`
- **All UUID versions from [RFC 9562](https://www.rfc-editor.org/rfc/rfc95629).**
- **Pydantic support.** [(Read more)](https://puuid.digon.io/quick_start/#pydantic-integration)
- **SQLAlchemy support.** [(Read more)](https://puuid.digon.io/quick_start/#sqlalchemy-integration)
- **Strong type guarantees!**

## Installation

```bash
pip install pUUID

# For SQLAlchemy support:
pip install 'pUUID[sqlalchemy]'
```

## Usage

Define a domain-specific ID by inheriting from a versioned base:

```python
from typing import Literal
from puuid import PUUIDv7

class UserUUID(PUUIDv7[Literal["user"]]):
    _prefix = "user"

# Generation
uid = UserUUID()
print(uid) # user_019b956e-ed25-70db-9d0a-0f30fb9047c2

# Deserialization
uid = UserUUID.from_string("user_019b956e-ed25-70db-9d0a-0f30fb9047c2")
```

## Resources

- [Online documentation](https://puuid.digon.io)
- [API Reference](https://puuid.digon.io/api_ref)
- [Changelog](https://puuid.digon.io/changelog)
- [Coverage Report](https://puuid.digon.io/changelog)
- [How to contribute](https://gitlab.com/DigonIO/puuid/-/blob/main/CONTRIBUTING.md)

## Sponsor

![Digon.IO GmbH Logo](https://gitlab.com/DigonIO/puuid/-/raw/main/assets/logo_digon.io_gmbh.png "Digon.IO GmbH")

Digon.IO provides dev & data end-to-end consulting for SMEs and software companies. [(Website)](https://digon.io) [(Technical Blog)](https://digon.io/en/blog)

_The sponsor logo is the property of Digon.IO GmbH. Standard trademark and copyright restrictions apply to any use outside this repository._

## License

- **Library source code:** Licensed under [LGPLv3](https://spdx.org/licenses/LGPL-3.0-only.html).
