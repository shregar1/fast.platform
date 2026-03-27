"""Load :mod:`sec.security.llm_provider_keys` without importing the ``security`` package.

Avoids ``src/sec/secrets`` shadowing the stdlib ``secrets`` module under pytest.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

# tests/sec/security/… → repo root is four levels up
_ROOT = Path(__file__).resolve().parents[3]
_LLM_KEYS = _ROOT / "src" / "fast_platform" / "sec" / "security" / "llm_provider_keys.py"
_spec = importlib.util.spec_from_file_location("fast_platform.sec.security.llm_provider_keys", _LLM_KEYS)
assert _spec and _spec.loader
_llm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_llm)

decrypt_api_key = _llm.decrypt_api_key
encrypt_api_key = _llm.encrypt_api_key
last_four = _llm.last_four
safe_decrypt = _llm.safe_decrypt
