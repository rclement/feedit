import os
import pytest

from typing import Any


is_ci = os.getenv("CI", "false") == "true"


@pytest.fixture(scope="session", autouse=True)
def vcr_config() -> dict[str, Any]:
    return dict(
        record_mode="none" if is_ci else "once",
        decode_compressed_response=True,
    )
