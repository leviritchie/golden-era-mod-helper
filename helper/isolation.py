"""Fail-closed write isolation for the creator helper.

Nothing in this package may write outside this clone's ``sandbox/`` folder.
"""

from __future__ import annotations

from pathlib import Path

from .paths import HELPER_ROOT, SANDBOX_DIR

FORBIDDEN_WRITE_MARKERS = (
    "Core.zip",
    "StreamingAssets",
    "GameAssembly.dll",
    "BepInEx",
)


class IsolationError(RuntimeError):
    """Raised when a path would leave the sandbox or look like a game install."""


def _resolve(path: Path | str) -> Path:
    return Path(path).expanduser().resolve()


def is_inside(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def assert_inside_helper(path: Path | str) -> Path:
    resolved = _resolve(path)
    if not is_inside(resolved, HELPER_ROOT):
        raise IsolationError(f"path is outside the helper root: {resolved}")
    return resolved


def assert_write_allowed(path: Path | str) -> Path:
    """Return a resolved path that is legal to create or overwrite."""
    resolved = _resolve(path)
    if not is_inside(resolved, SANDBOX_DIR):
        raise IsolationError(
            f"writes are only allowed under {SANDBOX_DIR}, not {resolved}"
        )
    parts = resolved.as_posix().split("/")
    for marker in FORBIDDEN_WRITE_MARKERS:
        if marker in parts:
            raise IsolationError(f"refusing write through forbidden marker {marker!r}: {resolved}")
    return resolved


def write_text(path: Path | str, contents: str, encoding: str = "utf-8") -> Path:
    target = assert_write_allowed(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(contents, encoding=encoding, newline="\n")
    return target


def write_bytes(path: Path | str, contents: bytes) -> Path:
    target = assert_write_allowed(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(contents)
    return target


def sandbox_join(*parts: str) -> Path:
    """Build a sandbox path from relative parts. Rejects `..` escapes."""
    if not parts:
        raise IsolationError("sandbox_join requires at least one path part")
    for part in parts:
        if not part or part in (".", "..") or "/" in part or "\\" in part:
            raise IsolationError(f"illegal sandbox path part: {part!r}")
    candidate = SANDBOX_DIR.joinpath(*parts)
    return assert_write_allowed(candidate)
