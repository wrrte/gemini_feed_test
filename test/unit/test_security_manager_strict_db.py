"""
Tests that demonstrate SecurityManager's current behaviour is unsafe

Rather than expecting specific exceptions from SecurityManager, these tests
use a STRICT DB test double that enforces invariants:

  * DB must never be asked to operate on unknown sensors.
  * DB must never be asked to remove unknown sensors.
  * DB must never be asked to update unknown zones.
  * DB must not be called for invalid security mode indices.

Failures in these tests come from the STRICT DB noticing invalid calls,
which shows that SecurityManager forwards bad operations to the DB instead
of rejecting them at the API boundary. The natural fix is to add explicit
checks and raise domain errors (exceptions) before touching the DB.
"""

import pytest

from core.security.security_exceptions import SensorAlreadyExistsError, SensorNotFoundError, SecurityZoneNotFoundError, \
    SecurityModeNotFoundError
from core.security.security_manager import SecurityManager
from core.security.security_memory_database import SecurityMemoryDatabase
from device.device_windoor_sensor import DeviceWinDoorSensor


class DummyLogManager:
    """
    Minimal stand-in for the real LogManager.

    Only the methods used by SecurityManager are implemented.
    """

    def __init__(self) -> None:
        self._time = 0
        self.logs = []

    def get_time(self):
        return self._time

    def save_log(self, log):
        self.logs.append(log)


class StrictSecurityDB(SecurityMemoryDatabase):
    """
    Test double that enforces 'safe' invariants.

    This behaves like SecurityMemoryDatabase, but raises AssertionError if
    SecurityManager attempts operations that a real DB SHOULD reject.

    Invariants enforced:
      * No duplicate sensors may be added.
      * turn_onoff_sensor() may only be called for known sensors.
      * remove_sensor() may only be called for known sensors.
      * set_now_security_mode() must not be called with an invalid index.
      * update_security_zone() must not be called for an unknown zone_id.
    """

    def add_sensor(self, sensor, on: bool = True, arm=None):
        # Invariant: no duplicate sensors allowed in DB
        if sensor in self.sensors:
            raise AssertionError("DB: duplicate sensor added")
        self.sensors[sensor] = (on, arm)

    def turn_onoff_sensor(self, sensor, onoff: bool) -> None:
        # Invariant: DB should only be called for known sensors
        if sensor not in self.sensors:
            raise AssertionError("DB: turn_onoff on unknown sensor")
        on, arm = self.sensors[sensor]
        self.sensors[sensor] = (onoff, arm)

    def remove_sensor(self, sensor):
        # Invariant: DB should not be asked to remove unknown sensors
        if sensor not in self.sensors:
            raise AssertionError("DB: remove unknown sensor")
        del self.sensors[sensor]

    def set_now_security_mode(self, now: int | None) -> None:
        # Invariant: if called with an index, it must be valid
        if now is not None and not (0 <= now < len(self.security_modes)):
            raise AssertionError("DB: invalid security mode index")
        self.now_security_mode = now

    def update_security_zone(self, zone_id, security_zone) -> None:
        # Invariant: zone_id must exist
        if zone_id < 0 or zone_id >= len(self.security_zones):
            raise AssertionError("DB: update unknown security zone")
        self.security_zones[zone_id] = security_zone


@pytest.fixture
def manager_with_strict_db():
    """
    Create a SecurityManager wired to StrictSecurityDB.

    Using this in tests lets us see when SecurityManager forwards
    invalid operations down to the DB layer.
    """
    db = StrictSecurityDB()
    log_mgr = DummyLogManager()
    mgr = SecurityManager(db, log_mgr)
    return mgr, db


# ---------------------------------------------------------------------------
# Sensor-related unsafe behaviours
# ---------------------------------------------------------------------------

def test_turn_on_unknown_sensor_calls_db(manager_with_strict_db):
    """
    Scenario:
      - The DB and SecurityManager know some initial sensors (from memory DB).
      - We call turn_on_sensor() with an unknown sensor.

    Expected contract:
      - SecurityManager should NOT ask the DB to update a sensor it doesn't know.
      - Call should be rejected (e.g. via domain exception) before DB is touched.

    Actual behaviour now:
      - SecurityManager skips the 'if sensor in self.sensors' body and
        STILL calls db_manager.turn_onoff_sensor(sensor, True).
      - StrictSecurityDB sees 'unknown sensor' and raises AssertionError.

    This failure shows:
      - Without validation (e.g. explicit exceptions in SecurityManager),
        invalid operations are forwarded to the DB, which is unsafe.
    """
    mgr, _ = manager_with_strict_db

    # Create a sensor NOT present in mgr.sensors / db.sensors
    unknown = DeviceWinDoorSensor(999, 999)

    with pytest.raises(SensorNotFoundError):
        mgr.turn_on_sensor(unknown)


def test_add_sensor_duplicate_causes_db_inconsistency(manager_with_strict_db):
    """
    Scenario:
      - A sensor is already known to SecurityManager (preloaded from DB).
      - We call add_sensor() again with the same sensor instance.

    Expected contract:
      - Either:
          * refuse the operation (e.g. DuplicateSensorError), OR
          * ensure both in-memory and DB stay consistent.
      - In any case, DB must not be asked to insert a duplicate.

    Actual behaviour now:
      - SecurityManager does NOT update self.sensors when the sensor is
        already present, but STILL calls db_manager.add_sensor(...).
      - StrictSecurityDB interprets this as a duplicate insert and
        raises AssertionError("DB: duplicate sensor added").

    This demonstrates that without explicit checks/exceptions at the
    SecurityManager level, DB integrity is at risk.
    """
    mgr, db = manager_with_strict_db

    # Take any existing sensor from the preloaded memory DB
    existing_sensor = next(iter(db.sensors.keys()))

    with pytest.raises(SensorAlreadyExistsError):
        mgr.add_sensor(existing_sensor)


def test_remove_unknown_sensor_forwards_invalid_operation(manager_with_strict_db):
    """
    Scenario:
      - We try to remove a sensor that neither SecurityManager nor DB knows.

    Expected contract:
      - The operation should be rejected cleanly (e.g. SensorNotFoundError)
        BEFORE the DB is touched.
      - DB must not get 'remove unknown sensor'.

    Actual behaviour now:
      - SecurityManager unconditionally calls db_manager.remove_sensor(sensor).
      - StrictSecurityDB raises AssertionError("DB: remove unknown sensor").

    This shows that currently, invalid removals reach the DB instead of being
    caught at the domain boundary.
    """
    mgr, _ = manager_with_strict_db
    unknown = DeviceWinDoorSensor(999, 999)

    with pytest.raises(SensorNotFoundError):
        mgr.remove_sensor(unknown)


# ---------------------------------------------------------------------------
# Security mode behaviour
# ---------------------------------------------------------------------------

def test_set_security_mode_index_out_of_range_still_hits_db(manager_with_strict_db):
    """
    Scenario:
      - There are N security modes.
      - Caller passes a mode index >= N (out of range).

    Desired safety property:
      - For invalid indices, SecurityManager should NOT call into the DB at all.
      - The call should be rejected at the SecurityManager boundary.

    Current behaviour:
      - SecurityManager ignores the 'if 0 <= mode < len(security_modes)' block
        and still calls db_manager.set_now_security_mode(self.now_security_mode),
        using a stale value.
      - We detect this by tracking calls to StrictSecurityDB.set_now_security_mode.

    The assertion that 'call_count == 0' will FAIL today, proving that invalid
    indices are propagated into the persistence layer instead of being rejected.
    """
    mgr, db = manager_with_strict_db
    original_now = db.now_security_mode

    invalid_index = len(db.security_modes) + 1  # definitely out of range

    # Track DB calls
    call_count = {"count": 0}
    original_set_now = db.set_now_security_mode

    def tracking_set_now(now):
        call_count["count"] += 1
        return original_set_now(now)

    db.set_now_security_mode = tracking_set_now  # monkey-patch in test

    with pytest.raises(SecurityModeNotFoundError):
        mgr.set_security_mode_index(invalid_index)

    # This assertion FAILS with the current implementation
    assert call_count["count"] == 0, "DB was called for invalid security mode index"
    assert db.now_security_mode == original_now


# ---------------------------------------------------------------------------
# Security zone behaviour
# ---------------------------------------------------------------------------

def test_arm_unknown_zone_hits_db(manager_with_strict_db):
    """
    Scenario:
      - arm_security_zone() is called with a non-existent zone_id.

    Expected safety:
      - Manager must confirm the zone exists and reject the call if it doesn't.
      - DB must not be asked to update an unknown zone.

    Current behaviour:
      - SecurityManager iterates over security_zones, finds no match, and
        (in the current code) still ends up calling into the DB.
      - StrictSecurityDB enforces 'no update for unknown zone' and raises.

    This shows that zone operations for invalid IDs are not safely guarded.
    """
    mgr, _ = manager_with_strict_db

    invalid_zone_id = 999  # larger than any valid zone id

    with pytest.raises(SecurityZoneNotFoundError):
        mgr.arm_security_zone(invalid_zone_id)
