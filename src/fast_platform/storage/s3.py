"""
AWS S3 integration
"""

from typing import Optional, BinaryIO, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class S3Object:
    """S3 object"""
    key: str
    bucket: str
    size: int
    last_modified: datetime
    etag: str
    metadata: Dict[str, str]


@dataclass
class PresignedUrl:
    """Presigned URL"""
    url: str
    expires_at: datetime


class S3Client:
    """
    AWS S3 client
    """
    
    def __init__(
        self,
        bucket: Optional[str] = None,
        region: str = "us-east-1",
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None
    ):
        self.bucket = bucket
        self.region = region
        self.access_key = access_key
        self.secret_key = secret_key
        self._client = None
        self._resource = None
    
    def _get_client(self):
        if self._client is None:
            try:
                import boto3
                session = boto3.Session(
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    region_name=self.region
                )
                self._client = session.client("s3")
                self._resource = session.resource("s3")
            except ImportError:
                raise ImportError("boto3 package required for S3Client")
        return self._client
    
    async def upload_file(
        self,
        key: str,
        file: BinaryIO,
        bucket: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None
    ) -> S3Object:
        """
        Upload a file to S3
        
        Args:
            key: Object key
            file: File-like object
            bucket: Bucket name (uses default if not provided)
            metadata: Object metadata
            content_type: MIME type
        """
        client = self._get_client()
        bucket_name = bucket or self.bucket
        
        if not bucket_name:
            raise ValueError("bucket required")
        
        extra_args = {}
        if metadata:
            extra_args["Metadata"] = metadata
        if content_type:
            extra_args["ContentType"] = content_type
        
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(
                pool,
                lambda: client.upload_fileobj(
                    file, bucket_name, key, ExtraArgs=extra_args
                )
            )
        
        # Get object info
        response = client.head_object(Bucket=bucket_name, Key=key)
        
        return S3Object(
            key=key,
            bucket=bucket_name,
            size=response["ContentLength"],
            last_modified=response["LastModified"],
            etag=response["ETag"].strip('"'),
            metadata=response.get("Metadata", {})
        )
    
    async def download_file(
        self,
        key: str,
        bucket: Optional[str] = None
    ) -> bytes:
        """Download a file from S3"""
        client = self._get_client()
        bucket_name = bucket or self.bucket
        
        if not bucket_name:
            raise ValueError("bucket required")
        
        import io
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        buffer = io.BytesIO()
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(
                pool,
                lambda: client.download_fileobj(bucket_name, key, buffer)
            )
        
        return buffer.getvalue()
    
    async def delete_file(
        self,
        key: str,
        bucket: Optional[str] = None
    ) -> bool:
        """Delete a file from S3"""
        client = self._get_client()
        bucket_name = bucket or self.bucket
        
        if not bucket_name:
            raise ValueError("bucket required")
        
        client.delete_object(Bucket=bucket_name, Key=key)
        return True
    
    async def list_files(
        self,
        prefix: str = "",
        bucket: Optional[str] = None,
        max_keys: int = 1000
    ) -> List[S3Object]:
        """List files in S3"""
        client = self._get_client()
        bucket_name = bucket or self.bucket
        
        if not bucket_name:
            raise ValueError("bucket required")
        
        response = client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix,
            MaxKeys=max_keys
        )
        
        objects = []
        for obj in response.get("Contents", []):
            objects.append(S3Object(
                key=obj["Key"],
                bucket=bucket_name,
                size=obj["Size"],
                last_modified=obj["LastModified"],
                etag=obj["ETag"].strip('"'),
                metadata={}
            ))
        
        return objects
    
    async def generate_presigned_url(
        self,
        key: str,
        expiration: int = 3600,
        bucket: Optional[str] = None,
        operation: str = "get_object"
    ) -> PresignedUrl:
        """
        Generate a presigned URL
        
        Args:
            key: Object key
            expiration: URL expiration in seconds
            bucket: Bucket name
            operation: S3 operation
        """
        client = self._get_client()
        bucket_name = bucket or self.bucket
        
        if not bucket_name:
            raise ValueError("bucket required")
        
        url = client.generate_presigned_url(
            ClientMethod=operation,
            Params={"Bucket": bucket_name, "Key": key},
            ExpiresIn=expiration
        )
        
        from datetime import timedelta
        
        return PresignedUrl(
            url=url,
            expires_at=datetime.utcnow() + timedelta(seconds=expiration)
        )
