"""AWS Lambda client."""

from typing import Optional, Dict, Any
import json


class LambdaClient:
    """AWS Lambda client."""

    def __init__(
        self,
        region: str = "us-east-1",
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ):
        """Execute __init__ operation.

        Args:
            region: The region parameter.
            access_key: The access_key parameter.
            secret_key: The secret_key parameter.
        """
        self.region = region
        self.access_key = access_key
        self.secret_key = secret_key
        self._client = None

    def _get_client(self):
        """Execute _get_client operation.

        Returns:
            The result of the operation.
        """
        if self._client is None:
            try:
                import boto3

                session = boto3.Session(
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    region_name=self.region,
                )
                self._client = session.client("lambda")

            except ImportError:
                raise ImportError("boto3 required for LambdaClient")

        return self._client

    async def invoke(
        self,
        function_name: str,
        payload: Optional[Dict[str, Any]] = None,
        invocation_type: str = "RequestResponse",  # RequestResponse, Event, DryRun
    ) -> Dict[str, Any]:
        """Invoke a Lambda function.

        Args:
            function_name: Function name or ARN
            payload: Function payload
            invocation_type: Invocation type

        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        client = self._get_client()

        params = {"FunctionName": function_name, "InvocationType": invocation_type}

        if payload:
            params["Payload"] = json.dumps(payload)

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            response = await loop.run_in_executor(pool, lambda: client.invoke(**params))

        # Parse response
        result = {
            "status_code": response["StatusCode"],
            "executed_version": response.get("ExecutedVersion"),
            "log_result": response.get("LogResult"),
        }

        # Read payload
        if "Payload" in response:
            payload_bytes = response["Payload"].read()
            try:
                result["payload"] = json.loads(payload_bytes)
            except json.JSONDecodeError:
                result["payload"] = payload_bytes.decode()

        return result

    async def invoke_async(
        self, function_name: str, payload: Optional[Dict[str, Any]] = None
    ) -> str:
        """Invoke a Lambda function asynchronously."""
        result = await self.invoke(function_name, payload, invocation_type="Event")
        return result.get("status_code", "")

    async def get_function(self, function_name: str) -> Dict[str, Any]:
        """Get function configuration."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        client = self._get_client()

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            response = await loop.run_in_executor(
                pool, lambda: client.get_function(FunctionName=function_name)
            )

        return response

    async def list_functions(self) -> list:
        """List all functions."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        client = self._get_client()

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            response = await loop.run_in_executor(pool, lambda: client.list_functions())

        return response.get("Functions", [])

    async def update_function_code(
        self,
        function_name: str,
        zip_file: Optional[bytes] = None,
        s3_bucket: Optional[str] = None,
        s3_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update function code."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        client = self._get_client()

        params = {"FunctionName": function_name}

        if zip_file:
            params["ZipFile"] = zip_file
        elif s3_bucket and s3_key:
            params["S3Bucket"] = s3_bucket
            params["S3Key"] = s3_key

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            response = await loop.run_in_executor(
                pool, lambda: client.update_function_code(**params)
            )

        return response
