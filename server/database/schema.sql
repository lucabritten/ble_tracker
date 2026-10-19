-- BLE-Raumtracker: Datenbankschema (PostgreSQL)
--
-- Schlüssel: Geräte, Knoten und Räume werden über ihren Kurznamen identifiziert.
-- Derselbe Name steht in der ESP-Config, in der MQTT-Nachricht und hier.
-- Eine technische ID gibt es nur bei den Massentabellen.
-- ON UPDATE CASCADE sorgt dafür, dass ein Umbenennen alle Verweise mitzieht.
--
-- Ausführen:  psql -d <datenbank> -f schema.sql
-- Mehrfach ausführbar dank IF NOT EXISTS.

-- ---------- Stammdaten ----------

CREATE TABLE IF NOT EXISTS rooms (
    name          TEXT PRIMARY KEY,
    display_name  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS esp_nodes (
    name       TEXT PRIMARY KEY,
    room_name  TEXT NOT NULL
               REFERENCES rooms (name) ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS devices (
    name          TEXT PRIMARY KEY,
    display_name  TEXT NOT NULL,
    irk           TEXT NOT NULL UNIQUE
                  CHECK (irk ~ '^[0-9A-Fa-f]{32}$')   -- 16 Byte als Hex
);

-- ---------- Rohmessungen (werden nach 7 Tagen gelöscht) ----------

CREATE TABLE IF NOT EXISTS detections (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    device_name    TEXT NOT NULL
                   REFERENCES devices (name) ON UPDATE CASCADE ON DELETE CASCADE,
    esp_node_name  TEXT NOT NULL
                   REFERENCES esp_nodes (name) ON UPDATE CASCADE ON DELETE CASCADE,
    rssi           SMALLINT NOT NULL CHECK (rssi BETWEEN -127 AND 20),
    arrival_time   TIMESTAMPTZ NOT NULL
);

-- für das Aufräumen nach Alter und für "Messungen von Gerät X im Zeitraum"
CREATE INDEX IF NOT EXISTS detections_arrival_time_idx
    ON detections (arrival_time);
CREATE INDEX IF NOT EXISTS detections_device_time_idx
    ON detections (device_name, arrival_time);

-- ---------- Aufenthalte ----------

CREATE TABLE IF NOT EXISTS stays (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    device_name  TEXT NOT NULL
                 REFERENCES devices (name) ON UPDATE CASCADE ON DELETE CASCADE,
    room_name    TEXT NOT NULL
                 REFERENCES rooms (name) ON UPDATE CASCADE,
    started_at   TIMESTAMPTZ NOT NULL,
    ended_at     TIMESTAMPTZ,                          -- NULL = Aufenthalt läuft noch
    CHECK (ended_at IS NULL OR ended_at >= started_at)
);

-- Pro Gerät darf höchstens ein Aufenthalt offen sein.
CREATE UNIQUE INDEX IF NOT EXISTS stays_one_open_per_device
    ON stays (device_name) WHERE ended_at IS NULL;

CREATE INDEX IF NOT EXISTS stays_device_started_idx
    ON stays (device_name, started_at);


-- ---------- Beispieldaten (zum Ausprobieren auskommentiert) ----------
-- INSERT INTO rooms (name, display_name) VALUES
--     ('kitchen', 'Küche'), ('bath', 'Bad'), ('living', 'Wohnzimmer');
-- INSERT INTO esp_nodes (name, room_name) VALUES
--     ('kitchen', 'kitchen'), ('bath', 'bath'), ('living', 'living');
-- INSERT INTO devices (name, display_name, irk) VALUES
--     ('luca-iphone', 'Lucas iPhone', '<32 Hex-Zeichen>');
