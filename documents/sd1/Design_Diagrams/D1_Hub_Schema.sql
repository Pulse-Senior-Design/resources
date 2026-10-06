-- D1 target schema. This file does not migrate an existing Hub database.
-- Apply it to a new database after the implementation follows the D1 contract.
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = FULL;
PRAGMA busy_timeout = 5000;

BEGIN IMMEDIATE;
CREATE TABLE origin (
    origin_id TEXT PRIMARY KEY NOT NULL
        CHECK(length(origin_id) BETWEEN 1 AND 64
              AND origin_id NOT GLOB '*[^A-Za-z0-9_-]*'),
    expected_sender BLOB NOT NULL CHECK(length(expected_sender) = 16)
);
CREATE TABLE sensor (
    origin_id TEXT NOT NULL,
    sensor_id TEXT NOT NULL
        CHECK(length(sensor_id) BETWEEN 1 AND 64
              AND sensor_id NOT GLOB '*[^A-Za-z0-9_-]*'),
    PRIMARY KEY (origin_id, sensor_id),
    FOREIGN KEY (origin_id) REFERENCES origin(origin_id) ON DELETE RESTRICT
);
CREATE TABLE envelope (
    origin_id TEXT NOT NULL,
    message_id TEXT NOT NULL CHECK(length(message_id) = 36),
    envelope_version INTEGER NOT NULL CHECK(envelope_version = 1),
    collected_at_ms INTEGER NOT NULL CHECK(collected_at_ms >= 0),
    received_at_ms INTEGER NOT NULL CHECK(received_at_ms > 0),
    authenticated_sender BLOB NOT NULL CHECK(length(authenticated_sender) = 16),
    envelope_bytes BLOB NOT NULL CHECK(length(envelope_bytes) > 0),
    PRIMARY KEY (origin_id, message_id),
    FOREIGN KEY (origin_id) REFERENCES origin(origin_id) ON DELETE RESTRICT
);
CREATE TABLE reading (
    origin_id TEXT NOT NULL,
    message_id TEXT NOT NULL,
    sensor_id TEXT NOT NULL,
    encoding TEXT NOT NULL CHECK(length(encoding) BETWEEN 1 AND 128),
    payload BLOB NOT NULL CHECK(length(payload) BETWEEN 1 AND 262144),
    PRIMARY KEY (origin_id, message_id, sensor_id),
    FOREIGN KEY (origin_id, message_id)
        REFERENCES envelope(origin_id, message_id) ON DELETE CASCADE,
    FOREIGN KEY (origin_id, sensor_id)
        REFERENCES sensor(origin_id, sensor_id) ON DELETE RESTRICT
);
CREATE INDEX envelope_origin_time
    ON envelope(origin_id, collected_at_ms, message_id);
CREATE INDEX reading_sensor_history
    ON reading(origin_id, sensor_id, message_id);
PRAGMA user_version = 1;
COMMIT;

-- The ingestion transaction checks sender equality, UUID syntax, sample count,
-- sensor uniqueness, decoder validity, and exact envelope content. SQL does
-- not enforce that an envelope has at least one child row. A2 does so before
-- committing the parent and all children together.
