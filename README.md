# pUUID

**pUUID** - Prefixed UUIDs for Python with **Pydantic** & **SQLAlchemy** support

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

- Prefixed UUID's for Python
  - Versions: 1, 3, 4, 5, 6, 7, 8
- Variable prefix length
- Supports **Pydantic**
- Supports **SQLAlchemy**
- Typing!

## When should I use pUUID?

Use **pUUID** when a plain UUIDs just isn’t expressive enough.

If this...

```text
b100f10f-6876-4b61-984f-2c74be42fcd4
```

...makes you ask "UUID of what, exactly?", and this...

```text
user_b100f10f-6876-4b61-984f-2c74be42fcd4
```

...makes you instantly happier, then **pUUID** is for you.

It’s especially useful when:

- You use FastAPI or some kind of Pydantic API
- Your database layer uses SQLAlchemy
- You want additional type safety and human-readable IDs
- You’ve ever mixed up an _user_id_ with a _group_id_

## Installing **pUUID** with pip

The **pUUID** library can be installed directly from the PyPI repositories with:

```bash
pip install pUUID
```

If you want to use the **SQLAlchemy** feature, you need to install the `sqlalchemy` dependency group:

```bash
pip install 'pUUID[sqlalchemy]'
```

## Sponsor

![Digon.IO GmbH Logo](https://gitlab.com/DigonIO/puuid/-/raw/main/assets/logo_digon.io_gmbh.png "Digon.IO GmbH")

Digon.IO provides dev & data end-to-end consulting for SMEs and software companies. [(Website)](https://digon.io) [(Technical Blog)](https://digon.io/en/blog)

_The sponsor logo is the property of Digon.IO GmbH. Standard trademark and copyright restrictions apply to any use outside this repository._

## License

- **Library source code:** Licensed under [LGPLv3](https://spdx.org/licenses/LGPL-3.0-only.html).
