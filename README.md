![Logo: pUUID - Prefixed UUIDs for Python](https://gitlab.com/DigonIO/puuid/-/raw/main/assets/logo_font_path.svg "pUUID Logo")

**pUUID** - Prefixed UUIDs for Python with **Pydantic** & **SQLAlchemy** support.

[![repository](https://img.shields.io/badge/src-GitLab-orange)](https://gitlab.com/DigonIO/puuid)
[![mirror](https://img.shields.io/badge/mirror-GitHub-orange)](https://github.com/DigonIO/puuid)
[![License: LGPLv3](https://gitlab.com/DigonIO/puuid/-/raw/main/assets/badges/license.svg)](https://spdx.org/licenses/LGPL-3.0-only.html)
[![pipeline status](https://gitlab.com/DigonIO/puuid/badges/main/pipeline.svg)](https://gitlab.com/DigonIO/puuid/-/pipelines)
[![coverage report](https://gitlab.com/DigonIO/puuid/badges/main/coverage.svg)](https://gitlab.com/DigonIO/puuid/-/pipelines)
[![Code style: black](https://gitlab.com/DigonIO/puuid/-/raw/main/assets/badges/black.svg)](https://github.com/psf/black)
[![Imports: isort](https://gitlab.com/DigonIO/puuid/-/raw/main/assets/badges/isort.svg)](https://pycqa.github.io/isort/)

[![pkgversion](https://img.shields.io/pypi/v/pUUID)](https://pypi.org/project/pUUID/)
[![versionsupport](https://img.shields.io/pypi/pyversions/pUUID)](https://pypi.org/project/pUUID/)
[![Downloads Week](https://pepy.tech/badge/puuid/week)](https://pepy.tech/project/puuid)
[![Downloads Total](https://pepy.tech/badge/puuid)](https://pepy.tech/project/puuid)

---

# pUUID - Prefixed UUIDs for Python

## Features

- **Human-Friendly:** `user_550e8400...` instead of just randomness.
- **Standard Compliant:** Supports all UUID versions from [RFC 9562](https://www.rfc-editor.org/rfc/rfc9562.html).
- **Pydantic support.** [(Read more)](https://puuid.digon.io/quick_start/#pydantic-integration)
- **SQLAlchemy support.** [(Read more)](https://puuid.digon.io/quick_start/#sqlalchemy-integration)
- **Strong type guarantees!**

## Motivation

Standard UUIDs like `019b9a2e-9856-737c-955e-c4e4523a2176` are great for machines but difficult for humans. **pUUID** implements prefixed identifiers (e.g., `user_019b9a2e...`) to provide:

- **Semantics & Context:** Immediately identify the resource type in logs, URLs, and databases without additional lookups.
- **Error Prevention:** Strong type guarantees prevent passing a `customer_id` into a `payment_id` field.
- **Improved UX:** Identifiers are easier to discuss, double-click to select (thanks to the underscore separator), and debug.

## Installation

```bash
# NOTE: pUUID requires python 3.14+
pip install pUUID

# For SQLAlchemy support:
pip install 'pUUID[sqlalchemy]'
```

## Usage

Define a domain-specific ID by inheriting from a versioned base:

```python
from typing import Literal
from puuid import PUUIDv7

UserUUID = PUUIDv7[Literal["user"]]

# Generation
uid = UserUUID()
print(uid) # user_019b956e-ed25-70db-9d0a-0f30fb9047c2

# Deserialization
uid2 = UserUUID.from_string("user_019b956e-ed25-70db-9d0a-0f30fb9047c2")
```

## Resources

- [Online documentation](https://puuid.digon.io)
- [API Reference](https://puuid.digon.io/api_ref)
- [Changelog](https://puuid.digon.io/changelog)
- [Coverage Report](https://puuid.digon.io/coverage)
- [How to contribute](https://gitlab.com/DigonIO/puuid/-/blob/main/CONTRIBUTING.md)

## Alternatives

If you only need lexicographically sortable IDs and want to build the **SQLAlchemy** support yourself, these two projects might be for you:

- [**TypeID**](https://github.com/akhundMurad/typeid-python) - **pUUID** supports all **UUID** versions because it uses Python’s standard `uuid` library for **UUID** generation, while **TypeID** uses a custom generator that comes with performance improvements but only supports **UUIDv7**. **TypeID** does not support **SQLAlchemy** out of the box.
- [**UPID**](https://github.com/carderne/upid) - **UPID** implements a modified version of the **ULID** standard, which was designed before **UUIDv7** was available. **UPID** does not support **SQLAlchemy** out of the box.

## Sponsor

![Digon.IO GmbH Logo](https://gitlab.com/DigonIO/puuid/-/raw/main/assets/logo_digon.io_gmbh.png "Digon.IO GmbH")

Digon.IO provides dev & data end-to-end consulting for SMEs and software companies. [(Website)](https://digon.io) [(Technical Blog)](https://digon.io/en/blog)

*The sponsor logo is the property of Digon.IO GmbH. Standard trademark and copyright restrictions apply to any use outside this repository.*

## License

- **Library source code:** Licensed under [LGPLv3](https://spdx.org/licenses/LGPL-3.0-only.html).
