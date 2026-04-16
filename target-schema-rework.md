# Target Schema Rework — `spec` JSONB for Type-Specific Fields

## Motivation

Current `targets` table has typed columns for SSH-specific fields (`address`, `username`, `credential_id`). HTTP targets have nowhere natural to store `url`, `auth_type`, `auth_variable_path`. As more target types are added (e.g., SNMP, MQTT, gRPC), adding per-type columns doesn't scale.

## Proposed Schema

```sql
CREATE TABLE targets (
    id          uuid PRIMARY KEY,
    name        VARCHAR(255) UNIQUE NOT NULL,
    target_type VARCHAR(50) NOT NULL,    -- "ssh", "http", future types
    spec        JSONB NOT NULL,          -- type-specific config
    metadata    JSONB,                   -- generic (description, labels, tags)
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    last_used_at TIMESTAMPTZ
);
```

### spec examples by type

**SSH:**
```json
{
  "address": "10.0.5.53",
  "username": "godon_robot",
  "credential_id": "550e8400-...",
  "allows_downtime": false
}
```

**HTTP:**
```json
{
  "url": "http://greenhouse:8090",
  "auth_type": "none",
  "auth_variable_path": null
}
```

## Repos Affected

| Repo | Files | Change |
|------|-------|--------|
| **godon-controller** | `database.py`, `target_create.py`, `target_get.py`, `targets_get.py`, `target_delete.py`, `breeder_service.py`, `config.py` | DDL, CRUD reads/writes spec, resolver branches on target_type, config validation |
| **godon-images** | `images/godon-api/openapi.yml`, `src/types.rs`, `src/handlers.rs`, `src/windmill_adapter.rs`, `shared/tests/stubs/controller/target_*.py`, `shared/tests/stubs/test-data/target-*.yaml` | API spec, Rust types, test stubs |
| **godon-cli** | `src/lib.rs` (Target struct), `src/main.rs` (formatters), `src/client.rs` (create_target_from_yaml) | Target struct uses spec, YAML parsing, display formatting |
| **godon-images/godon-mcp** | `src/tools.rs` | target_create tool schema, required fields |
| **godon** | `examples/network.yml`, `examples/greenhouse.yml` | Already using targetRefs, no change needed |
| **godon-breeders** | `effectuation/http.py`, `effectuation/ssh.py` (if exists) | **No change** — resolver still produces same resolved dict |
| **godon-charts** | DB init/migration | Schema update in chart |
| **godon-test-infra** | Test targets, fixtures | Update target creation payloads |
| **godon-controller/tests** | `test_targets.py`, `test_config_validation.py` | Update assertions for spec-based fields |

## Key Design Decisions

1. **Resolver output unchanged** — `breeder_service.py._resolve_target_refs()` reads from `spec` JSONB but still produces the same resolved dict (`{address, username, credentialId}` for SSH, `{url, auth_type}` for HTTP). Breeders are decoupled from the schema.

2. **`metadata` vs `spec`** — `spec` is the type-specific config (required, validated per type). `metadata` is optional generic info (description, labels, tags). Both JSONB.

3. **API validation** — `target_create` validates `spec` required fields based on `target_type`:
   - SSH: `address` required, `username` required
   - HTTP: `url` required

4. **CLI YAML format** — user writes type-specific fields at top level, CLI packs into spec:
   ```yaml
   name: greenhouse
   targetType: http
   url: "http://greenhouse:8090"
   auth_type: none
   ```
   becomes `{"spec": {"url": "http://greenhouse:8090", "auth_type": "none"}, ...}`

5. **Migration** — existing targets with typed columns need migration:
   ```sql
   -- Add new columns
   ALTER TABLE targets ADD COLUMN spec JSONB;
   ALTER TABLE targets ADD COLUMN metadata JSONB;
   -- Migrate existing rows
   UPDATE targets SET spec = jsonb_build_object(
     'address', address,
     'username', username,
     'credential_id', credential_id,
     'allows_downtime', allows_downtime
   ) WHERE target_type = 'ssh';
   UPDATE targets SET metadata = jsonb_build_object(
     'description', description
   );
   -- Drop old columns
   ALTER TABLE targets DROP COLUMN address;
   ALTER TABLE targets DROP COLUMN username;
   ALTER TABLE targets DROP COLUMN credential_id;
   ALTER TABLE targets DROP COLUMN allows_downtime;
   ALTER TABLE targets DROP COLUMN description;
   ```

## Implementation Order

1. godon-controller: DDL + CRUD scripts + resolver + config validation
2. godon-controller: tests
3. godon-images: API spec + Rust types + handlers + test stubs
4. godon-cli: Target struct + formatters + YAML parsing
5. godon-images/godon-mcp: tool schema update
6. godon-charts: migration
7. godon-test-infra: fixture updates
8. Integration test
