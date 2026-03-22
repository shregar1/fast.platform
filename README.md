# fast-platform

Single installable distribution (**`pip install fast-platform`**) that bundles many former standalone `fast_*` modules **unchanged at import time** (flat top-level imports such as `from notifications import …`, `from db import …`).

Logical organization is defined by the **package taxonomy** in [`src/fast_platform/taxonomy.py`](src/fast_platform/taxonomy.py). Imports stay flat under `src/`; the taxonomy is used for docs, tests layout, and navigation.

## Package taxonomy

Each top-level name under `src/` belongs to exactly one **section** (`PackageSection`). The canonical mapping is `PACKAGE_TO_SECTION` in `fast_platform.taxonomy`.

| Section | Meaning |
|--------|---------|
| **core** | Config, DTOs, errors, helpers, orchestration services |
| **security** | Crypto, API keys, identity, secret backends |
| **persistence** | SQLAlchemy + multi-backend datastores |
| **data_platform** | Search, vectors, object storage, cache |
| **messaging** | Queues, Kafka, jobs, events, notifications, webhooks |
| **realtime** | Channels, streams, WebRTC |
| **integrations** | LLM, payments, media, analytics, admin |
| **operations** | Observability, OpenTelemetry, flags, tenancy, resilience, API versioning |

### Packages by section

| Section | Packages |
|--------|----------|
| **core** | `configuration`, `dtos`, `errors`, `utils`, `services`, `fast_platform` |
| **security** | `security`, `secrets`, `identity` |
| **persistence** | `db`, `datastores` |
| **data_platform** | `search`, `vectors`, `storage`, `cache` |
| **messaging** | `kafka`, `queues`, `events`, `jobs`, `notifications`, `webhooks` |
| **realtime** | `channels`, `streams`, `webrtc` |
| **integrations** | `llm`, `payments`, `media`, `analytics`, `admin` |
| **operations** | `observability`, `otel`, `resilience`, `tenancy`, `versioning`, `features` |

Use in code:

```python
from fast_platform.taxonomy import section_of, PackageSection

section_of("notifications")  # PackageSection.MESSAGING
```

## Layout: `src/` vs `tests/`

- **`src/`** — **flat** top-level packages (`configuration/`, `notifications/`, …) so existing imports remain stable.
- **`tests/`** — mirrors the taxonomy: **`tests/<section_folder>/<package>/`**. Section folder names come from `SECTION_TEST_FOLDER` in `taxonomy.py` (e.g. `core`, `persistence`, `data_platform`). The security section uses **`sec`** (not `security`) so the `security` package can live at `tests/sec/security/` without a path collision.

Example: tests for `utils` live under `tests/core/utils/`; tests for `notifications` under `tests/messaging/notifications/`.

## Highlights (by import name)

| Import | Role |
|--------|------|
| `configuration` | JSON config loaders + Pydantic DTOs per subsystem |
| `dtos` | Shared Pydantic DTOs (`IDTO` base) |
| `errors` | Structured HTTP-oriented exceptions (`BadInputError`, `NotFoundError`, …) |
| `notifications` | Email/SMS/push templates, fan-out, idempotency, preferences (`pip install fast-platform[jinja2]` for templating extras) |
| `resilience` | Circuit breakers, retries, bulkheads |
| `versioning` | API versioning (`VersionedAPIRouter`, `VersioningMiddleware`, path/header/query strategies) |
| `features` | In-app feature flags, rollout, targeting |
| `channels` | Real-time hub, Redis/Kafka backends, presence, ACLs, metrics |
| `db` | SQLAlchemy engine, sessions, `DBDependency` |
| `datastores` | `IDataStore` adapters (Redis, Mongo, ES, …) |
| `observability` | Logging, metrics, tracing, audit, OTLP |
| `admin` | Admin API router (users, roles, audit log), generic SQLAlchemy CRUD routers |
| `queues` | Queues (DLQ, envelope, backends) |
| `jobs` | Background jobs |
| `storage` | Object storage (S3, GCS, Azure) |
| `secrets` | Secret backends + cache (Vault, AWS, GCP; not the stdlib `secrets` module) |
| `vectors` | Vector stores |
| `tenancy` | Multi-tenant context |
| `webhooks` | Webhook signing / delivery |
| `webrtc` | WebRTC signaling |
| `llm` | LLM providers, tools, streaming |
| `kafka` | Kafka producer/consumer, outbox |
| `identity` | OAuth/OIDC, JWKS, API keys |
| `media` | Uploads, variants, presigned URLs |
| `payments` | Payment gateways, webhooks, SCA |
| `search` | Meilisearch, Typesense, OpenSearch |
| `security` | API keys, inbound webhooks, field encryption |

**Install:** `pip install fast-platform`

Optional backends: e.g. `pip install fast-platform[async,otel,rabbitmq,s3,openai,meilisearch,pillow]`.

`pyfastmvc` depends on this wheel for these modules instead of many separate distributions.
