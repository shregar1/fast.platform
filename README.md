# fast-platform

Single installable distribution (**`pip install fast-platform`**) that bundles many former standalone `*` packages **unchanged at import time**, including **`notifications`**, **`admin`**, **`resilience`**, **`versioning`**, and **`features`**, alongside DB, queues, observability, and the rest of the table below.

| Import | Role |
|--------|------|
| `errors` | Structured HTTP-oriented exceptions (`BadInputError`, `NotFoundError`, …) |
| `notifications` | Email/SMS/push templates, fan-out, idempotency, preferences (`pip install fast-platform[jinja2]` for templating extras) |
| `resilience` | Circuit breakers, retries, bulkheads |
| `versioning` | API versioning (`VersionedAPIRouter`, `VersioningMiddleware`, path/header/query strategies) |
| `features` | In-app feature flags, rollout, targeting |
| `channels` | Real-time hub, Redis/Kafka backends, presence, ACLs, metrics |
| `db` | SQLAlchemy engine, sessions, `DBDependency` |
| `datastores` | `IDataStore` adapters (Redis, Mongo, ES, …) |
| `observability` | Logging, metrics, tracing, audit, OTLP |
| `analytics` | HTTP sink, sampling, PII scrub, schema registry |
| `admin` | Admin API router (users, roles, audit log), generic SQLAlchemy CRUD routers |
| `queues` | Queues (DLQ, envelope, backends) |
| `jobs` | Background jobs |
| `storage` | Object storage (S3, GCS, Azure) |
| `secrets` | Secrets + cache |
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
