"""Cross-cutting constants for fast_platform."""

from __future__ import annotations

from typing import Final

# HTTP headers
HEADER_AUTHORIZATION: Final[str] = "Authorization"
HEADER_CONTENT_TYPE: Final[str] = "Content-Type"
HEADER_X_TENANT_ID: Final[str] = "X-Tenant-ID"
HEADER_X_WEBHOOK_SIGNATURE: Final[str] = "X-Webhook-Signature"
HEADER_WWW_AUTHENTICATE: Final[str] = "WWW-Authenticate"
HEADER_X_API_KEY: Final[str] = "X-API-Key"
HEADER_X_SIGNATURE: Final[str] = "X-Signature"
HEADER_X_TIMESTAMP: Final[str] = "X-Timestamp"
HEADER_USER_AGENT: Final[str] = "user-agent"
HEADER_X_FORWARDED_FOR: Final[str] = "X-Forwarded-For"
HEADER_X_REAL_IP: Final[str] = "X-Real-IP"
HEADER_X_USER_ID: Final[str] = "x-user-id"
HEADER_X_FASTMVC_PRIMARY_QUEUE: Final[str] = "x-fastmvc-primary-queue"

# Content types
CONTENT_TYPE_APPLICATION_JSON: Final[str] = "application/json"
CONTENT_TYPE_TEXT_PLAIN: Final[str] = "text/plain"
CONTENT_TYPE_FORM_URLENCODED: Final[str] = "application/x-www-form-urlencoded"

# Common defaults
DEFAULT_ENCODING: Final[str] = "utf-8"
ASCII_ENCODING: Final[str] = "ascii"
DEFAULT_HOST: Final[str] = "localhost"
DEFAULT_REDIS_PORT: Final[int] = 6379
DEFAULT_REDIS_URL: Final[str] = "redis://localhost:6379/0"
DEFAULT_AWS_REGION: Final[str] = "us-east-1"
SERVICE_NAME: Final[str] = "fastmvc"

# LLM providers
OPENAI_PROVIDER: Final[str] = "openai"
ANTHROPIC_PROVIDER: Final[str] = "anthropic"
GEMINI_PROVIDER: Final[str] = "gemini"
GROQ_PROVIDER: Final[str] = "groq"
MISTRAL_PROVIDER: Final[str] = "mistral"
OLLAMA_PROVIDER: Final[str] = "ollama"

# HTTP status codes
HTTP_OK: Final[int] = 200
HTTP_BAD_REQUEST: Final[int] = 400
HTTP_UNAUTHORIZED: Final[int] = 401
HTTP_FORBIDDEN: Final[int] = 403
HTTP_NOT_FOUND: Final[int] = 404
HTTP_CONFLICT: Final[int] = 409
HTTP_TOO_MANY_REQUESTS: Final[int] = 429
HTTP_INTERNAL_SERVER_ERROR: Final[int] = 500
HTTP_BAD_GATEWAY: Final[int] = 502
HTTP_SERVICE_UNAVAILABLE: Final[int] = 503
HTTP_REQUEST_TIMEOUT: Final[int] = 408
HTTP_NOT_IMPLEMENTED: Final[int] = 501

# Time constants (seconds)
DEFAULT_TIMEOUT_SECONDS: Final[float] = 5.0
DEFAULT_READ_TIMEOUT: Final[float] = 10.0
DEFAULT_LONG_TIMEOUT_SECONDS: Final[float] = 30.0
HALF_SECOND: Final[float] = 0.5
TENTH_OF_A_SECOND: Final[float] = 0.1
ONE_MINUTE_SECONDS: Final[int] = 60
FIVE_MINUTES_SECONDS: Final[int] = 300
ONE_HOUR_SECONDS: Final[int] = 3600
ONE_DAY_SECONDS: Final[int] = 86400

# Size / count constants
DEFAULT_LIMIT: Final[int] = 1000
DEFAULT_PAGE_SIZE: Final[int] = 100
DEFAULT_LARGE_LIMIT: Final[int] = 10000
BYTES_PER_KB: Final[int] = 1024
AES_KEY_SIZE_BITS: Final[int] = 256
AES_GCM_NONCE_LENGTH: Final[int] = 12
AES_256_KEY_LENGTH_BYTES: Final[int] = 32
AES_128_KEY_LENGTH_BYTES: Final[int] = 16
DEFAULT_SALT_LENGTH: Final[int] = 16
DEFAULT_PBKDF2_ITERATIONS: Final[int] = 100_000
API_KEY_LENGTH_BYTES: Final[int] = 32
FERNET_KEY_LENGTH_BYTES: Final[int] = 32
LLM_DEFAULT_MAX_TOKENS: Final[int] = 256
DEFAULT_API_KEY_EXPIRY_DAYS: Final[int] = 365
DEFAULT_HASH_ALGORITHM: Final[str] = "sha256"
DEFAULT_SQLITE_URL_PREFIX: Final[str] = "sqlite:///"
BYTES_PER_KB: Final[int] = 1024
MEMORY_BACKEND: Final[str] = "memory"
OLLAMA_DEFAULT_BASE_URL: Final[str] = "http://localhost:11434"
MAX_KEYS_VALIDATION_ERROR: Final[str] = "max_keys must be >= 1"

# Field names
TENANT_ID_FIELD: Final[str] = "tenant_id"
USER_ID_FIELD: Final[str] = "user_id"
API_KEY_FIELD: Final[str] = "api_key"

# Log levels
LOG_LEVEL_INFO: Final[str] = "info"
LOG_LEVEL_WARNING: Final[str] = "warning"

# Environment
ENV_PRODUCTION: Final[str] = "production"

# SQL
HEALTH_CHECK_SQL: Final[str] = "SELECT 1"

# Error messages
NOT_FOUND_MESSAGE: Final[str] = "Not found"
UNKNOWN_ERROR: Final[str] = "Unknown error"
VALIDATION_EXTRACTION_ERROR: Final[str] = "Could not extract data for validation"
MAX_KEYS_VALIDATION_ERROR: Final[str] = "max_keys must be >= 1"

# Metrics descriptions
HTTP_REQUESTS_TOTAL_DESCRIPTION: Final[str] = "Total HTTP requests"
HTTP_REQUEST_DURATION_DESCRIPTION: Final[str] = "HTTP request duration in seconds"

# Ports
DEFAULT_SMTP_PORT: Final[int] = 587
HTTPS_PORT: Final[int] = 443
