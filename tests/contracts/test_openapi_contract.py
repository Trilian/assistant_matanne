"""Tests de contrat OpenAPI (contrat OpenAPI).

Utilise Schemathesis sur endpoint public `/health` pour valider
la conformité entre spec OpenAPI et réponse réelle ASGI.
"""

from __future__ import annotations

import pytest
schemathesis = pytest.importorskip("schemathesis")

from src.api.main import app

schema = schemathesis.from_asgi("/openapi.json", app)


@pytest.mark.contract
@schema.parametrize(method="GET", endpoint="/health")
def test_contrat_endpoint_health(case: schemathesis.Case) -> None:
    response = case.call_asgi()
    case.validate_response(response)
