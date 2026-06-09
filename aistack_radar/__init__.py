"""Checkout shim for running ``python -m aistack_radar`` without install."""

from pathlib import Path
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)  # type: ignore[name-defined]
_src_pkg = Path(__file__).resolve().parent.parent / "src" / "aistack_radar"
if _src_pkg.exists():
    __path__.append(str(_src_pkg))  # type: ignore[name-defined]

