# Detection Rounds Table

## Schema (in shared archive_db)

```sql
CREATE TABLE IF NOT EXISTS detection_rounds (
    round_id        SERIAL PRIMARY KEY,
    sender_id       VARCHAR(255) NOT NULL,
    status          TEXT NOT NULL DEFAULT 'active',  -- active / completed
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_detection_rounds_active 
    ON detection_rounds (status) WHERE status = 'active';
```

## Breeder Mode Logic

At each trial start, breeder queries:

```sql
SELECT sender_id FROM detection_rounds WHERE status = 'active' LIMIT 1;
```

- No rows → mode = `optimize` (default)
- Row exists and `sender_id == my_id` → mode = `impulse`
- Row exists and `sender_id != my_id` → mode = `hold`

## Round Completion

After the sender executes its impulse trial, it marks the round completed:

```sql
UPDATE detection_rounds SET status = 'completed', completed_at = NOW() 
WHERE sender_id = %s AND status = 'active';
```

The next round (if any) becomes visible on the next trial cycle.
