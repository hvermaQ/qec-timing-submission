"""Name -> factory registry for every pluggable component.

A new code, noise model, backend, decoder, extractor, analysis or idle source is
added by decorating its factory; nothing else in the package needs to change.

    @register("code", "repetition")
    class RepetitionCode: ...

    code = create("code", "repetition", d=5)

Registration only makes a component discoverable. Whether it behaves correctly is
checked by `qec_timing.testing.contracts`, which every registered component of a
kind must pass.
"""

from __future__ import annotations

from typing import Any, Callable, Literal

Kind = Literal["code", "noise", "backend", "decoder", "extractor", "analysis", "idle_source"]
KINDS: tuple[Kind, ...] = ("code", "noise", "backend", "decoder", "extractor", "analysis",
                           "idle_source")

_REGISTRY: dict[str, dict[str, Callable[..., Any]]] = {k: {} for k in KINDS}


def register(kind: Kind, name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator: register `factory` under (kind, name). Names are unique per kind."""
    if kind not in _REGISTRY:
        raise ValueError(f"unknown kind {kind!r}; expected one of {KINDS}")

    def deco(factory: Callable[..., Any]) -> Callable[..., Any]:
        if name in _REGISTRY[kind]:
            raise ValueError(f"{kind} {name!r} is already registered")
        _REGISTRY[kind][name] = factory
        return factory

    return deco


def create(kind: Kind, name: str, /, **params: Any) -> Any:
    """Build the registered component (kind, name) with `params`."""
    try:
        factory = _REGISTRY[kind][name]
    except KeyError:
        raise KeyError(f"no {kind} named {name!r}; available: {available(kind)}") from None
    return factory(**params)


def available(kind: Kind) -> list[str]:
    return sorted(_REGISTRY[kind])


def unregister(kind: Kind, name: str) -> None:
    """Remove a registration (tests use this to stay independent of each other)."""
    _REGISTRY[kind].pop(name, None)
