import json
import pytest

from storage.storage_sqlite import StorageManager
from storage.security_storage_sqlite import SecuritySqliteDB
from storage.log_storage_sqlite import LogSqliteDB
from core.log.log_manager import LogManager
from core.security.security_manager import SecurityManager
from core.security.security_zone_geometry.area import Square


@pytest.fixture
def storage_manager(tmp_path):
    # 각 테스트마다 새 sqlite 파일을 사용
    db_path = tmp_path / "test_safehome.db"
    # 사용자가 말한 초기화 방식
    return StorageManager("src/init.sql", str(db_path))


@pytest.fixture
def sqlite_security_manager(storage_manager):
    security_db = SecuritySqliteDB(storage_manager)
    log_db = LogSqliteDB(storage_manager)
    log_manager = LogManager(log_db)
    return SecurityManager(security_db, log_manager)


def test_sqlite_security_manager_loads_from_db(sqlite_security_manager):
    manager = sqlite_security_manager

    # 최소한 하나 이상의 센서와 모드가 로딩되어야 한다.
    assert isinstance(manager.sensors, dict)
    assert len(manager.sensors) > 0

    assert isinstance(manager.security_modes, list)
    assert len(manager.security_modes) > 0

    # now_security_mode는 None 이거나 유효한 인덱스여야 한다.
    mode = manager.now_security_mode
    if mode is not None:
        assert 0 <= mode < len(manager.security_modes)


def test_turn_onoff_sensor_persists_to_sqlite(sqlite_security_manager, storage_manager):
    manager = sqlite_security_manager

    sensor = next(iter(manager.sensors.keys()))
    sensor_id = sensor.get_id()

    # 센서를 끄면 DB에도 반영되어야 한다.
    manager.turn_off_sensor(sensor)

    rows = storage_manager.execute(
        "SELECT is_enabled FROM sensors WHERE sensor_id=?", (sensor_id,)
    )
    assert rows
    assert bool(rows[0][0]) is False

    # 같은 DB로 새 매니저를 만들면 꺼진 상태로 로딩되어야 한다.
    manager2 = SecurityManager(
        SecuritySqliteDB(storage_manager),
        LogManager(LogSqliteDB(storage_manager)),
    )
    sensor2 = next(s for s in manager2.sensors.keys() if s.get_id() == sensor_id)
    assert manager2.sensors[sensor2][0] is False

    # 다시 켜기
    manager2.turn_on_sensor(sensor2)
    rows = storage_manager.execute(
        "SELECT is_enabled FROM sensors WHERE sensor_id=?", (sensor_id,)
    )
    assert bool(rows[0][0]) is True


def test_set_arm_persists_to_sqlite(sqlite_security_manager, storage_manager):
    manager = sqlite_security_manager

    sensor = next(iter(manager.sensors.keys()))
    sensor_id = sensor.get_id()

    # arm = True
    manager.set_arm(sensor, True)
    rows = storage_manager.execute(
        "SELECT is_armed FROM sensors WHERE sensor_id=?", (sensor_id,)
    )
    assert rows
    assert bool(rows[0][0]) is True

    # arm = False
    manager.set_arm(sensor, False)
    rows = storage_manager.execute(
        "SELECT is_armed FROM sensors WHERE sensor_id=?", (sensor_id,)
    )
    assert bool(rows[0][0]) is False

    # arm = None -> DB에는 NULL 이어야 한다.
    manager.set_arm(sensor, None)
    rows = storage_manager.execute(
        "SELECT is_armed FROM sensors WHERE sensor_id=?", (sensor_id,)
    )
    assert rows[0][0] is None


def test_set_security_mode_index_persists_to_sqlite(sqlite_security_manager, storage_manager):
    manager = sqlite_security_manager

    assert len(manager.security_modes) > 0

    manager.set_security_mode_index(0)

    rows = storage_manager.execute(
        "SELECT value FROM system_settings WHERE name=?", ("now_security_mode",)
    )
    assert rows
    value = json.loads(rows[0][0])
    assert value["mode"] == 0

    # 새 매니저에서도 그대로 로딩되는지 확인
    manager2 = SecurityManager(
        SecuritySqliteDB(storage_manager),
        LogManager(LogSqliteDB(storage_manager)),
    )
    assert manager2.now_security_mode == 0


def test_add_update_remove_security_zone_persists_to_sqlite(sqlite_security_manager, storage_manager):
    manager = sqlite_security_manager

    # 새 존 추가
    zone = manager.add_security_zone()

    rows = storage_manager.execute(
        "SELECT security_zone_id, is_enabled, up_left_x, up_left_y, "
        "down_right_x, down_right_y "
        "FROM security_zones WHERE security_zone_id=?",
        (zone.id,),
    )
    assert rows
    row = rows[0]

    assert row[0] == zone.id
    assert bool(row[1]) is zone.enabled
    assert (row[2], row[3]) == zone.area.up_left
    assert (row[4], row[5]) == zone.area.down_right

    # 센서 매핑도 security_zone_sensor_map 에 있어야 한다.
    rows = storage_manager.execute(
        "SELECT sensor_id FROM security_zone_sensor_map WHERE security_zone_id=?",
        (zone.id,),
    )
    db_sensor_ids = {r[0] for r in rows}
    zone_sensor_ids = {s.get_id() for s in zone.sensors}
    assert db_sensor_ids == zone_sensor_ids

    # 영역 업데이트
    new_area = Square(
        zone.area.up_left[0] + 10,
        zone.area.up_left[1] + 10,
        zone.area.down_right[0] + 10,
        zone.area.down_right[1] + 10,
    )
    manager.update_security_zone(zone.id, new_area)

    rows = storage_manager.execute(
        "SELECT up_left_x, up_left_y, down_right_x, down_right_y "
        "FROM security_zones WHERE security_zone_id=?",
        (zone.id,),
    )
    assert rows
    (ux, uy, dx, dy) = rows[0]
    assert (ux, uy) == new_area.up_left
    assert (dx, dy) == new_area.down_right

    # 삭제
    manager.remove_security_zone(zone.id)

    rows = storage_manager.execute(
        "SELECT COUNT(*) FROM security_zones WHERE security_zone_id=?",
        (zone.id,),
    )
    assert rows[0][0] == 0

    rows = storage_manager.execute(
        "SELECT COUNT(*) FROM security_zone_sensor_map WHERE security_zone_id=?",
        (zone.id,),
    )
    assert rows[0][0] == 0


def test_persistence_across_system_restart(tmp_path):
    # 1. 첫 실행 - DB 생성 및 상태 변경
    db_path = tmp_path / "safehome.db"
    storage1 = StorageManager("src/init.sql", str(db_path))
    manager1 = SecurityManager(
        SecuritySqliteDB(storage1),
        LogManager(LogSqliteDB(storage1)),
    )

    # 상태를 몇 개 바꿔둔다
    sensor = next(iter(manager1.sensors.keys()))
    manager1.turn_off_sensor(sensor)
    manager1.set_arm(sensor, True)
    if manager1.security_modes:
        manager1.set_security_mode_index(0)
    zone = manager1.add_security_zone()

    # 2. 시스템 “재시작” - 새 StorageManager, 새 DB 객체, 새 SecurityManager
    storage2 = StorageManager("src/init.sql", str(db_path))
    manager2 = SecurityManager(
        SecuritySqliteDB(storage2),
        LogManager(LogSqliteDB(storage2)),
    )

    # 3. 재시작 후에도 상태가 그대로인지 확인
    sensor2 = next(s for s in manager2.sensors.keys() if s.get_id() == sensor.get_id())
    assert manager2.sensors[sensor2][0] is False      # is_enabled
    assert manager2.sensors[sensor2][1] is True       # is_armed

    if manager1.security_modes:
        assert manager2.now_security_mode == 0

    zone2 = next(z for z in manager2.security_zones if z.id == zone.id)
    assert zone2.enabled == zone.enabled
    assert zone2.area.up_left == zone.area.up_left
    assert zone2.area.down_right == zone.area.down_right


def test_security_mode_applies_arming_even_after_restart(tmp_path):
    # 같은 db 파일을 공유하면서 두 번 "실행"할 것
    db_path = tmp_path / "safehome.db"

    # 1차 실행 - DB 생성 및 모드 설정
    storage1 = StorageManager("src/init.sql", str(db_path))
    manager1 = SecurityManager(
        SecuritySqliteDB(storage1),
        LogManager(LogSqliteDB(storage1)),
    )

    # init.sql에 모드가 없으면 이 테스트는 의미 없음
    if not manager1.security_modes:
        pytest.skip("init.sql에 security mode가 없음")

    # zone 영향은 빼고 모드만 보려고 전부 비활성화
    for z in manager1.security_zones:
        z.disable()

    # 테스트할 모드 인덱스 (필요하면 0,1,2 다 돌도록 for 루프로 바꿔도 됨)
    target_index = 0

    # now_security_mode를 DB에 저장
    manager1.set_security_mode_index(target_index)

    # 2차 실행 - 완전 재시작 느낌으로 새 StorageManager, 새 SecurityManager
    storage2 = StorageManager("src/init.sql", str(db_path))
    manager2 = SecurityManager(
        SecuritySqliteDB(storage2),
        LogManager(LogSqliteDB(storage2)),
    )

    # DB에서 now_security_mode가 제대로 복원됐는지
    assert manager2.now_security_mode == target_index

    # 다시 zone 영향 제거
    for z in manager2.security_zones:
        z.disable()

    # 선택된 모드
    mode = manager2.security_modes[target_index]

    # 모드 적용
    manager2.update()

    # 기대치: mode.get_arm_sensors()에 들어있는 센서들만 arm돼 있어야 함
    expected_ids = {s.get_id() for s in mode.get_arm_sensors()}
    armed_ids = {
        s.get_id()
        for s in manager2.sensors.keys()
        if s.test_armed_state()
    }

    assert armed_ids == expected_ids
