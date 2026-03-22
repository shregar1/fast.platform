"""
fast_vectors – Vector stores (Pinecone, Qdrant, Weaviate) for FastMVC.
"""

from fast_platform import (
    VectorsConfiguration,
    VectorsConfigurationDTO,
    PineconeConfigDTO,
    QdrantConfigDTO,
    WeaviateConfigDTO,
)

from .base import IVectorStore, build_vector_store
from .names import prefixed_collection_name, sanitize_collection_segment

__version__ = "0.1.1"

__all__ = [
    "IVectorStore",
    "VectorsConfiguration",
    "VectorsConfigurationDTO",
    "PineconeConfigDTO",
    "QdrantConfigDTO",
    "WeaviateConfigDTO",
    "build_vector_store",
    "prefixed_collection_name",
    "sanitize_collection_segment",
]
