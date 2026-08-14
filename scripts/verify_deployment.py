"""Public deployment smoke tests for EvidencePilot AI.

Built for Huzaifa Waqar Butt's recruiter-facing release. The script uses only
the Python standard library so it can run from GitHub Actions without setup.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_URL = "https://evidencepilot-ai.onrender.com"
FRONTEND_URL = "https://huzaifa-170504.github.io/evidencepilot-ai/"
FRONTEND_ORIGIN = "https://huzaifa-170504.github.io"


def fetch(url: str, *, accept: str = "application/json") -> tuple[int, dict[str, str], bytes]:
    request = Request(
        url,
        headers={
            "Accept": accept,
            "Origin": FRONTEND_ORIGIN,
            "User-Agent": "EvidencePilot-Deployment-Smoke-Test/1.0",
        },
    )
    with urlopen(request, timeout=30) as response:
        headers = {key.lower(): value for key, value in response.headers.items()}
        return response.status, headers, response.read()


def wait_for(
    label: str,
    check: Callable[[], None],
    *,
    attempts: int,
    delay_seconds: int,
) -> None:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            check()
            print(f"PASS {label}")
            return
        except (AssertionError, HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < attempts:
                print(f"WAIT {label} ({attempt}/{attempts}): {exc}")
                time.sleep(delay_seconds)
    raise RuntimeError(f"FAIL {label}: {last_error}")


def json_endpoint(path: str) -> tuple[dict[str, Any], dict[str, str]]:
    status, headers, body = fetch(f"{API_URL}{path}")
    assert status == 200, f"expected HTTP 200, received {status}"
    return json.loads(body), headers


def check_health() -> None:
    payload, headers = json_endpoint("/health")
    assert payload["status"] == "healthy"
    assert payload["service"] == "EvidencePilot AI API"
    assert headers.get("access-control-allow-origin") == FRONTEND_ORIGIN


def check_readiness() -> None:
    payload, _ = json_endpoint("/ready")
    assert payload["ready"] is True
    assert payload["dependencies"]["database"] == "supabase"
    assert payload["dependencies"]["document_storage"] == "supabase-private"


def check_demo() -> None:
    payload, _ = json_endpoint("/api/v1/demo")
    assert payload["status"] == "completed"
    assert payload["sources"], "demo has no sources"
    assert payload["claims"], "demo has no claims"
    assert payload["report_markdown"], "demo has no report"


def check_docs() -> None:
    status, _, body = fetch(f"{API_URL}/docs", accept="text/html")
    assert status == 200
    assert b"Swagger UI" in body


def check_frontend() -> None:
    status, _, body = fetch(FRONTEND_URL, accept="text/html")
    assert status == 200
    assert b"EvidencePilot AI" in body
    assert b"/evidencepilot-ai/assets/" in body


def main() -> None:
    wait_for("Render health and CORS", check_health, attempts=12, delay_seconds=10)
    wait_for("Render readiness", check_readiness, attempts=3, delay_seconds=5)
    wait_for("public demo API", check_demo, attempts=3, delay_seconds=5)
    wait_for("OpenAPI documentation", check_docs, attempts=3, delay_seconds=5)
    wait_for("GitHub Pages frontend", check_frontend, attempts=6, delay_seconds=10)
    print("EvidencePilot AI deployment is operational.")


if __name__ == "__main__":
    main()
