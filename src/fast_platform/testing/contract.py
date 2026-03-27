"""Contract testing."""

from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from functools import wraps
import json


@dataclass
class Contract:
    """API contract definition."""

    consumer: str
    provider: str
    request: Dict[str, Any]
    response: Dict[str, Any]


class ContractTester:
    """Contract testing for APIs.

    Validates that providers meet the contracts expected by consumers.
    """

    def __init__(self, provider: str):
        """Execute __init__ operation.

        Args:
            provider: The provider parameter.
        """
        self.provider = provider
        self._contracts: list = []

    def add_contract(self, contract: Contract) -> None:
        """Add a contract."""
        self._contracts.append(contract)

    async def verify(self, client: Any) -> Dict[str, Any]:
        """Verify all contracts.

        Args:
            client: HTTP client to use for verification

        Returns:
            Verification results

        """
        results = []

        for contract in self._contracts:
            try:
                # Make request
                response = await client.request(
                    method=contract.request.get("method", "GET"),
                    url=contract.request.get("path", "/"),
                    headers=contract.request.get("headers", {}),
                    json=contract.request.get("body"),
                )

                # Verify response
                expected = contract.response
                actual = {
                    "status": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.json()
                    if response.headers.get("content-type", "").startswith("application/json")
                    else response.text,
                }

                # Check status code
                if "status" in expected and expected["status"] != actual["status"]:
                    results.append(
                        {
                            "contract": f"{contract.consumer}->{contract.provider}",
                            "passed": False,
                            "error": f"Expected status {expected['status']}, got {actual['status']}",
                        }
                    )
                    continue

                results.append(
                    {"contract": f"{contract.consumer}->{contract.provider}", "passed": True}
                )

            except Exception as e:
                results.append(
                    {
                        "contract": f"{contract.consumer}->{contract.provider}",
                        "passed": False,
                        "error": str(e),
                    }
                )

        return {
            "provider": self.provider,
            "total": len(results),
            "passed": sum(1 for r in results if r["passed"]),
            "failed": sum(1 for r in results if not r["passed"]),
            "results": results,
        }


def contract_test(provider: str, consumer: Optional[str] = None, pact_file: Optional[str] = None):
    """Decorator for contract tests.

    Args:
        provider: Provider service name
        consumer: Consumer service name
        pact_file: Path to pact file

    """

    def decorator(func: Callable):
        """Execute decorator operation.

        Args:
            func: The func parameter.

        Returns:
            The result of the operation.
        """
        func._is_contract_test = True
        func._contract_provider = provider
        func._contract_consumer = consumer
        func._contract_pact_file = pact_file
        return func

    return decorator
