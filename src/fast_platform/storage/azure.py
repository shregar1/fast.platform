"""
Azure Blob Storage integration
"""

from typing import Optional, BinaryIO, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AzureBlob:
    """Azure blob"""
    name: str
    container: str
    size: int
    last_modified: datetime
    etag: str


class AzureBlobClient:
    """
    Azure Blob Storage client
    """
    
    def __init__(
        self,
        connection_string: Optional[str] = None,
        account_name: Optional[str] = None,
        account_key: Optional[str] = None,
        container: Optional[str] = None
    ):
        self.connection_string = connection_string
        self.account_name = account_name
        self.account_key = account_key
        self.container = container
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            try:
                from azure.storage.blob import BlobServiceClient
                
                if self.connection_string:
                    self._client = BlobServiceClient.from_connection_string(
                        self.connection_string
                    )
                else:
                    from azure.core.credentials import AzureNamedKeyCredential
                    credential = AzureNamedKeyCredential(
                        self.account_name,
                        self.account_key
                    )
                    self._client = BlobServiceClient(
                        f"https://{self.account_name}.blob.core.windows.net",
                        credential=credential
                    )
            except ImportError:
                raise ImportError("azure-storage-blob required for AzureBlobClient")
        return self._client
    
    async def upload_file(
        self,
        name: str,
        file: BinaryIO,
        container: Optional[str] = None,
        overwrite: bool = True
    ) -> AzureBlob:
        """Upload a file to Azure Blob Storage"""
        client = self._get_client()
        container_name = container or self.container
        
        if not container_name:
            raise ValueError("container required")
        
        blob_client = client.get_blob_client(container_name, name)
        
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(
                pool,
                lambda: blob_client.upload_blob(file, overwrite=overwrite)
            )
        
        props = blob_client.get_blob_properties()
        
        return AzureBlob(
            name=props.name,
            container=container_name,
            size=props.size,
            last_modified=props.last_modified,
            etag=props.etag
        )
    
    async def download_file(
        self,
        name: str,
        container: Optional[str] = None
    ) -> bytes:
        """Download a file from Azure Blob Storage"""
        client = self._get_client()
        container_name = container or self.container
        
        if not container_name:
            raise ValueError("container required")
        
        blob_client = client.get_blob_client(container_name, name)
        
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool,
                blob_client.download_blob().readall
            )
    
    async def delete_file(
        self,
        name: str,
        container: Optional[str] = None
    ) -> bool:
        """Delete a file from Azure Blob Storage"""
        client = self._get_client()
        container_name = container or self.container
        
        if not container_name:
            raise ValueError("container required")
        
        blob_client = client.get_blob_client(container_name, name)
        blob_client.delete_blob()
        
        return True
    
    async def generate_sas_url(
        self,
        name: str,
        expiry_hours: int = 1,
        container: Optional[str] = None
    ) -> str:
        """Generate a SAS URL"""
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions
        from datetime import timedelta
        
        container_name = container or self.container
        
        if not container_name:
            raise ValueError("container required")
        
        sas_token = generate_blob_sas(
            account_name=self.account_name,
            container_name=container_name,
            blob_name=name,
            account_key=self.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
        )
        
        return f"https://{self.account_name}.blob.core.windows.net/{container_name}/{name}?{sas_token}"
