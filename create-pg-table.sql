DROP SCHEMA IF EXISTS "analise-comparativa-dbs" CASCADE;

CREATE SCHEMA "analise-comparativa-dbs";

DROP TABLE IF EXISTS "analise-comparativa-dbs".logs;

CREATE TABLE "analise-comparativa-dbs".logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    log_level VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    source VARCHAR(255) NOT NULL,
    test_id BIGINT NOT NULL
);

CREATE INDEX idx_logs_timestamp ON "analise-comparativa-dbs".logs(timestamp);
CREATE INDEX idx_logs_log_level ON "analise-comparativa-dbs".logs(log_level);