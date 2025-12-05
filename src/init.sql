-- SQLite database export
PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "sensors" (
    "sensor_id" INTEGER PRIMARY KEY NOT NULL,
    "sensor_type" VARCHAR NOT NULL,
    "location" VARCHAR NOT NULL,
    "is_enabled" BOOLEAN NOT NULL,
    "is_armed" BOOLEAN 
);


CREATE TABLE IF NOT EXISTS "cameras" (
    "camera_id" INTEGER PRIMARY KEY NOT NULL,
    "location_x" INTEGER NOT NULL,
    "location_y" INTEGER NOT NULL,
    "pan_angle" INTEGER NOT NULL,
    "zoom_level" INTEGER NOT NULL,
    "password" VARCHAR,
    "enabled" BOOLEAN NOT NULL
);


CREATE TABLE IF NOT EXISTS "users" (
    "user_id" VARCHAR PRIMARY KEY NOT NULL,
    "password" VARCHAR
);


CREATE TABLE IF NOT EXISTS "mode_sensor_map" (
    "id" INTEGER PRIMARY KEY NOT NULL,
    "mode_id" INTEGER NOT NULL,
    "sensor_id" INTEGER NOT NULL,
    FOREIGN KEY("mode_id") REFERENCES "safehome_modes"("mode_id"),
    FOREIGN KEY("sensor_id") REFERENCES "sensors"("sensor_id")
);


CREATE TABLE IF NOT EXISTS "system_settings" (
    "id" INTEGER PRIMARY KEY NOT NULL,
    "name" VARCHAR NOT NULL,
    "value" VARCHAR
);

-- Indexes
CREATE UNIQUE INDEX IF NOT EXISTS "system_settings_index_2"
ON "system_settings" ("name");

CREATE TABLE IF NOT EXISTS "safehome_modes" (
    "mode_id" INTEGER PRIMARY KEY NOT NULL,
    "name" VARCHAR NOT NULL UNIQUE
);

-- Indexes
CREATE UNIQUE INDEX IF NOT EXISTS "safehome_modes_index_2"
ON "safehome_modes" ("name");

CREATE TABLE IF NOT EXISTS "logs" (
    "log_id" INTEGER PRIMARY KEY NOT NULL,
    "date_time" DATETIME NOT NULL,
    "description" VARCHAR NOT NULL
);


CREATE TABLE IF NOT EXISTS "security_zones" (
    "security_zone_id" INTEGER PRIMARY KEY NOT NULL,
    "is_enabled" BOOLEAN NOT NULL,
    "up_left_x" FLOAT NOT NULL,
    "up_left_y" FLOAT NOT NULL,
    "down_right_x" FLOAT NOT NULL,
    "down_right_y" FLOAT NOT NULL
);


CREATE TABLE IF NOT EXISTS "security_zone_sensor_map" (
    "id" INTEGER PRIMARY KEY NOT NULL,
    "security_zone_id" INTEGER NOT NULL,
    "sensor_id" INTEGER NOT NULL,
    FOREIGN KEY("security_zone_id") REFERENCES "security_zones"("security_zone_id") ON DELETE CASCADE,
    FOREIGN KEY("sensor_id") REFERENCES "sensors"("sensor_id")
);

INSERT INTO "cameras" ("location_x", "location_y", "pan_angle", "zoom_level", "password", "enabled") VALUES (110, 50,  0, 2, ""    , TRUE );
INSERT INTO "cameras" ("location_x", "location_y", "pan_angle", "zoom_level", "password", "enabled") VALUES (220, 180, 0, 2, "1234", TRUE );
INSERT INTO "cameras" ("location_x", "location_y", "pan_angle", "zoom_level", "password", "enabled") VALUES (390, 250, 0, 2, ""    , FALSE);

INSERT INTO "users" ("user_id", "password") VALUES ("admin", "1234");
INSERT INTO "users" ("user_id", "password") VALUES ("guest", null  );


INSERT INTO "sensors" ("sensor_id", "sensor_type", "location", "is_enabled", "is_armed") 
VALUES (1, "DeviceWinDoorSensor" , '{"x": 20, "y": 80}', TRUE, null);
INSERT INTO "sensors" ("sensor_id", "sensor_type", "location", "is_enabled", "is_armed") 
VALUES (2, "DeviceWinDoorSensor" , '{"x": 70, "y": 20}', TRUE, null);
INSERT INTO "sensors" ("sensor_id", "sensor_type", "location", "is_enabled", "is_armed") 
VALUES (3, "DeviceWinDoorSensor" , '{"x": 20, "y": 200}', TRUE, null);
INSERT INTO "sensors" ("sensor_id", "sensor_type", "location", "is_enabled", "is_armed") 
VALUES (4, "DeviceWinDoorSensor" , '{"x": 400, "y": 20}', TRUE, null);
INSERT INTO "sensors" ("sensor_id", "sensor_type", "location", "is_enabled", "is_armed") 
VALUES (5, "DeviceWinDoorSensor" , '{"x": 470, "y": 80}', TRUE, null);
INSERT INTO "sensors" ("sensor_id", "sensor_type", "location", "is_enabled", "is_armed") 
VALUES (6, "DeviceWinDoorSensor" , '{"x": 475, "y": 210}', TRUE, null);
INSERT INTO "sensors" ("sensor_id", "sensor_type", "location", "is_enabled", "is_armed") 
VALUES (7, "DeviceWinDoorSensor" , '{"x": 250, "y": 20}', TRUE, null);
INSERT INTO "sensors" ("sensor_id", "sensor_type", "location", "is_enabled", "is_armed") 
VALUES (8, "DeviceWinDoorSensor" , '{"x": 80, "y": 280}', TRUE, null);
INSERT INTO "sensors" ("sensor_id", "sensor_type", "location", "is_enabled", "is_armed") 
VALUES (9, "DeviceMotionDetector", '{"up_left_x": 30, "up_left_y": 80, "down_right_x": 465, "down_right_y": 80}'     , TRUE, null);
INSERT INTO "sensors" ("sensor_id", "sensor_type", "location", "is_enabled", "is_armed") 
VALUES (10, "DeviceMotionDetector", '{"up_left_x": 145, "up_left_y": 170, "down_right_x": 25, "down_right_y": 248}', TRUE, null);

INSERT INTO "safehome_modes" ("mode_id", "name") VALUES (1, "Home");
INSERT INTO "safehome_modes" ("mode_id", "name") VALUES (2, "Away");
INSERT INTO "safehome_modes" ("mode_id", "name") VALUES (3, "Overnight");
INSERT INTO "safehome_modes" ("mode_id", "name") VALUES (4, "Extended");

INSERT INTO "mode_sensor_map" ("mode_id", "sensor_id") VALUES (2, 1);
INSERT INTO "mode_sensor_map" ("mode_id", "sensor_id") VALUES (2, 2);
INSERT INTO "mode_sensor_map" ("mode_id", "sensor_id") VALUES (2, 3);
INSERT INTO "mode_sensor_map" ("mode_id", "sensor_id") VALUES (2, 4);
INSERT INTO "mode_sensor_map" ("mode_id", "sensor_id") VALUES (2, 5);
INSERT INTO "mode_sensor_map" ("mode_id", "sensor_id") VALUES (2, 6);
INSERT INTO "mode_sensor_map" ("mode_id", "sensor_id") VALUES (2, 7);
INSERT INTO "mode_sensor_map" ("mode_id", "sensor_id") VALUES (2, 8);
INSERT INTO "mode_sensor_map" ("mode_id", "sensor_id") VALUES (2, 9);
INSERT INTO "mode_sensor_map" ("mode_id", "sensor_id") VALUES (2, 10);

INSERT INTO "mode_sensor_map" ("mode_id", "sensor_id") VALUES (3, 1);
INSERT INTO "mode_sensor_map" ("mode_id", "sensor_id") VALUES (3, 2);
INSERT INTO "mode_sensor_map" ("mode_id", "sensor_id") VALUES (3, 3);
INSERT INTO "mode_sensor_map" ("mode_id", "sensor_id") VALUES (3, 4);
INSERT INTO "mode_sensor_map" ("mode_id", "sensor_id") VALUES (3, 5);
INSERT INTO "mode_sensor_map" ("mode_id", "sensor_id") VALUES (3, 6);
INSERT INTO "mode_sensor_map" ("mode_id", "sensor_id") VALUES (3, 7);
INSERT INTO "mode_sensor_map" ("mode_id", "sensor_id") VALUES (3, 8);

INSERT INTO "mode_sensor_map" ("mode_id", "sensor_id") VALUES (4, 7);
INSERT INTO "mode_sensor_map" ("mode_id", "sensor_id") VALUES (4, 8);
INSERT INTO "mode_sensor_map" ("mode_id", "sensor_id") VALUES (4, 9);
INSERT INTO "mode_sensor_map" ("mode_id", "sensor_id") VALUES (4, 10);

INSERT INTO "system_settings" ("name", "value") VALUES ("system_lock_time"           , '{"time": 300}');
INSERT INTO "system_settings" ("name", "value") VALUES ("panic_phone_number"         , '{"phone_number": "112"}');
INSERT INTO "system_settings" ("name", "value") VALUES ("alarm_time_before_phonecall", '{"time": 5}');
INSERT INTO "system_settings" ("name", "value") VALUES ("home_phone_number"          , '{"phone_number": "01012345678"}');
INSERT INTO "system_settings" ("name", "value") VALUES ("now_security_mode"          , '{"mode": null}');
INSERT INTO "system_settings" ("name", "value") VALUES ("master_password"            , '{"password": "1234"}');
INSERT INTO "system_settings" ("name", "value") VALUES ("guest_password"             , '{"password": ""}');

COMMIT;

