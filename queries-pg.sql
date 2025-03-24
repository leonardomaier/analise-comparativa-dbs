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


INSERT INTO "analise-comparativa-dbs".logs (timestamp, log_level, message, source, test_id)
SELECT
	timestamp '2020-01-10 20:00:00' +
       random() * (timestamp '2020-01-20 20:00:00' -
                   timestamp '2024-01-10 10:00:00'),                               
    '${log_level}',
    'Random log message: ${__Random(1,1000,)}',     
    'Source: ${source}',             
    ${__Random(1,10,)}                          
FROM generate_series(1,10);


UPDATE "analise-comparativa-dbs".logs
SET message = 'Updated log message'
WHERE id = (SELECT id FROM "analise-comparativa-dbs".logs ORDER BY RANDOM() LIMIT 1);

SELECT * FROM "analise-comparativa-dbs".logs
WHERE log_level = 'INFO';

SELECT * FROM "analise-comparativa-dbs".logs
WHERE log_level = 'ERROR';

SELECT * FROM "analise-comparativa-dbs".logs
WHERE log_level = 'WARN';

SELECT log_level, COUNT(*) AS log_count
FROM "analise-comparativa-dbs".logs
GROUP BY log_level
ORDER BY log_count DESC;

SELECT log_level,
       COUNT(*) AS log_count,
       ROUND((COUNT(*) * 100.0 / total.total_logs), 2) AS percentage
FROM "analise-comparativa-dbs".logs,
     (SELECT COUNT(*) AS total_logs FROM "analise-comparativa-dbs".logs) total
GROUP BY log_level, total.total_logs
ORDER BY percentage DESC;

SELECT * FROM "analise-comparativa-dbs".logs
WHERE log_level = 'ERROR'
ORDER BY timestamp DESC
LIMIT 100;

SELECT source, COUNT(*) as source_count
FROM "analise-comparativa-dbs".logs
GROUP BY source
ORDER BY source_count DESC
LIMIT 10;