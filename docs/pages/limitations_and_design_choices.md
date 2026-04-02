# Limitations & Design Choices

As a utility library with strong coupling to python's static typing features, `pUUID` has tried multiple approaches at the edges of what the type system allows. Below are some choices we had to make when confronted with certain interactions and what they mean in terms of usability.

## Generic Aliases vs. Nominal Types

In the initial release, the syntax was straight forward, but came with some unfortunate duplication:

```{.python notest}
class UserUUID(PUUIDv7[Literal["user"]]):
    _prefix = "user"
```

With the following release, the `_prefix` attribute was inferred by `__class_getitem__` magic, which generated concrete classes on the fly. This seemed handy at first glance, because it made the following two usages possible:

```{.python notest}
class UserUUID(PUUIDv7[Literal["user"]]): ...

DocumentUUID = PUUIDv4[Literal["doc"]]
```

This was workable during runtime for integrations with [SQLAlachemy](https://www.sqlalchemy.org/), [Pydantic](https://docs.pydantic.dev/latest/) and [FastAPI](https://fastapi.tiangolo.com/), but had one massive drawback. While the following code runs as intended with this approach, the type checkers think otherwise:

```{.python notest}
# Mypy/Pyright Error: Parameterized generics cannot be used with instance checks
if isinstance(uid, DocumentUUID): ...

# Mypy/Pyright Error: Class pattern class must not be a type alias
match uid:
    case DocumentUUID(): ...
```

While concise the `DocumentUUID = PUUIDv4[Literal["doc"]]`, syntax conflicts heavily with [PEP 484](https://peps.python.org/pep-0484/) and [PEP 585](https://peps.python.org/pep-0484/), which do not allow `isinstance()` checks on a `GenericAlias`.

We decided, that having the type checker scream at simple `isinstance()` invocation and just placing type ignore comments was something we did not want downstream to fight with. We tried out Metaclass based alternatives, which worked to some degree for at least one of the type-checkers (pyright), but the resulting implementation appeared even more brittle, than the previous solution.

## Back to Classes

The `v2.0.0` release reverts the `__class_getitem__` magic and thus no longer allows the previously introduced short-hand syntax and the intended usage becomes:

```{.python notest}
class UserUUID(PUUIDv4[Literal["user"]]): ...
```

The newly released implementation comes with the following consequences:

- The `"user"` prefix is now extracted using `__init_subclass__`, therefore avoiding the need for setting `_prefix = "user"` like in the initial release.
- FastAPI and Pydantic will just work with `pUUID`
- No more type checker complaints with `isinstance` and `match`.

### Class Identity Limitation

In the previous implementation, `PUUIDv4[Literal["user"]] is PUUIDv4[Literal["user"]]` would evaluate to `True`.

As there now is no longer a prefix-cache, `isinstance` checks will now return `False`, if multiple such definition exists across different modules and they are checked against each other. You therefore must define your specialized prefixed ID classes (e.g. `UserUUID`) exactly once in your project and import from there. Otherwise you might run into the surprise shown in the example below:

```{.python notest}
# Module A
class UserUUID(PUUIDv4[Literal["user"]]): ...

# Module B
class UserUUID(PUUIDv4[Literal["user"]]): ...

# These are NOT the same class!
uid_a = ModuleA.UserUUID()
isinstance(uid_a, ModuleB.UserUUID) # False
```

While this is a change compared to previous behaviour, python users should generally not be surprised by this, as this is how classes in python generally behave.
