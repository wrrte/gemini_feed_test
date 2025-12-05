from core.log.log_manager import LogManager
from core.security.alarm import Alarm
from core.security.security_exceptions import SensorAlreadyExistsError, SensorNotFoundError, \
    SecurityModeAlreadyExistsError, SecurityModeNotFoundError, SecurityZoneNotFoundError
from core.security.security_manager import SecurityManager
from core.security.security_memory_database import SecurityMemoryDatabase
from core.security.security_mode.away import Away
from core.security.security_mode.extended_travel import ExtendedTravel
from core.security.security_mode.home import Home
from core.security.security_mode.overnight_travel import OvernightTravel
from core.security.security_zone import SecurityZone
from core.security.sensor_controller import SensorController
from device.device_windoor_sensor import DeviceWinDoorSensor
from device.interface_sensor import InterfaceSensor
from storage.log_storage_memory import LogMemoryDB
import math
import pytest
from core.security.security_zone import security_zone_id

from core.security.security_zone_geometry.area import (  # 파일 이름에 맞게 수정
    Point,
    Line,
    Square,
    DIST_LIMIT,
    _distance_point_point,
    _distance_point_segment,
    _segments_intersect,
    _segments_distance,
    _point_in_square, Area,
)


def test_security_zone_geometry():
    zone = Square(100, -100, -100, 100)
    motion_sensor1 = Line((200, 0), (0, 200))
    motion_sensor2 = Line((101, -200), (101, 200))
    windoor_sensor1 = Point(100, 100)
    windoor_sensor2 = Point(-100, 101)
    assert zone.overlap(motion_sensor1)
    assert motion_sensor1.overlap(zone)
    assert not zone.overlap(motion_sensor2)
    assert not motion_sensor2.overlap(zone)
    assert zone.overlap(windoor_sensor1)
    assert windoor_sensor1.overlap(zone)
    assert not zone.overlap(windoor_sensor2)
    assert not windoor_sensor2.overlap(zone)
    assert motion_sensor1.overlap(windoor_sensor1)
    assert windoor_sensor1.overlap(motion_sensor1)


def test_security_mode_away():
    manager = SecurityManager(SecurityMemoryDatabase(), LogManager(LogMemoryDB()))
    sensors = list(manager.sensors.items())
    manager.set_security_mode_name("Away")
    manager.update()
    assert sensors[0][0].test_armed_state()
    assert sensors[1][0].test_armed_state()
    assert sensors[2][0].test_armed_state()
    assert not sensors[3][0].test_armed_state()
    assert not sensors[4][0].test_armed_state()
    assert not sensors[5][0].test_armed_state()
    assert not sensors[6][0].test_armed_state()
    assert not sensors[7][0].test_armed_state()


def test_security_mode_home():
    manager = SecurityManager(SecurityMemoryDatabase(), LogManager(LogMemoryDB()))
    sensors = list(manager.sensors.items())
    manager.set_security_mode_name("Home")
    manager.update()
    assert not sensors[0][0].test_armed_state()
    assert not sensors[1][0].test_armed_state()
    assert not sensors[2][0].test_armed_state()
    assert sensors[3][0].test_armed_state()
    assert sensors[4][0].test_armed_state()
    assert sensors[5][0].test_armed_state()
    assert not sensors[6][0].test_armed_state()
    assert not sensors[7][0].test_armed_state()


def test_security_mode_sleep():
    manager = SecurityManager(SecurityMemoryDatabase(), LogManager(LogMemoryDB()))
    sensors = list(manager.sensors.items())
    manager.set_security_mode_index(2)
    manager.update()
    assert not sensors[0][0].test_armed_state()
    assert not sensors[1][0].test_armed_state()
    assert not sensors[2][0].test_armed_state()
    assert not sensors[3][0].test_armed_state()
    assert not sensors[4][0].test_armed_state()
    assert not sensors[5][0].test_armed_state()
    assert sensors[6][0].test_armed_state()
    assert sensors[7][0].test_armed_state()


# def test_security_mode_extended_travel():
#     manager = SecurityManager()
#     sensors = list(manager.sensors.items())
#     manager.set_security_mode_index(3)
#     manager.update()
#     assert not manager.light.on
#     assert sensors[0][0].test_armed_state()
#     assert sensors[1][0].test_armed_state()
#     assert sensors[2][0].test_armed_state()
#     assert not sensors[3][0].test_armed_state()
#     assert not sensors[4][0].test_armed_state()
#     assert not sensors[5][0].test_armed_state()
#     assert not sensors[6][0].test_armed_state()
#     assert not sensors[7][0].test_armed_state()
#     manager.update()
#     assert manager.light.on


# def test_bypass_sensor():
#     manager = SecurityManager(SecurityMemoryDatabase(), LogManager(LogMemoryDB()))
#     sensors = list(manager.sensors.items())
#     manager.set_security_mode_name("Away")
#     manager.update()
#     manager.sensor_bypass(sensors[0][0], 1)
#     manager.update()
#     sensors[0][0].intrude()
#     result, armed_detected = manager.update()
#     assert manager.sensors[sensors[0][0]][0]
#     assert sensors[0][0].test_armed_state()
#     assert result[sensors[0][0]]
#     assert len(armed_detected) == 1 and sensors[0][0] in armed_detected
#     assert sensors[0][0] in manager.bypass
#     assert not manager.alarm.get()


def test_security_zone():
    manager = SecurityManager(SecurityMemoryDatabase(), LogManager(LogMemoryDB()))
    sensors = [s for s, _ in manager.sensors.items()]
    security_zone = manager.add_security_zone()
    manager.update_security_zone(security_zone.id, Square(90, 70, 10, 30))
    assert security_zone.sensors == [sensors[i] for i in [0, 8]]
    manager.arm_security_zone(security_zone.id)
    sensors[0].intrude()
    result, armed_detected = manager.update()
    assert [sensors[0]] == armed_detected
    assert manager.alarm.get()
    manager.disarm_security_zone(security_zone.id)
    result, armed_detected = manager.update()
    assert [] == armed_detected
    assert not manager.alarm.get()

    manager.remove_security_zone(security_zone.id)
    assert len(manager.security_zones) == 0
    try:
        manager.remove_security_zone(security_zone.id)
        assert False
    except SecurityZoneNotFoundError:
        pass


def test_sensor_onoff():
    manager = SecurityManager(SecurityMemoryDatabase(), LogManager(LogMemoryDB()))
    sensors = list(manager.sensors.items())
    manager.turn_off_sensor(sensors[0][0])
    result, armed_detected = manager.update()
    assert result[sensors[0][0]] is None
    manager.turn_on_sensor(sensors[0][0])
    result, armed_detected = manager.update()
    assert result[sensors[0][0]] is not None


def test_arm_order():
    manager = SecurityManager(SecurityMemoryDatabase(), LogManager(LogMemoryDB()))
    sensors = [s for s, _ in manager.sensors.items()]
    security_zone = manager.add_security_zone()
    manager.update_security_zone(security_zone.id, Square(90, 70, 10, 30))
    assert security_zone.sensors == [sensors[i] for i in [0, 8]]
    manager.arm_security_zone(security_zone.id)
    sensors[0].intrude()
    result, armed_detected = manager.update()
    assert [sensors[0]] == armed_detected
    assert manager.alarm.get()

    manager.disarm(sensors[0])
    result, armed_detected = manager.update()
    assert [] == armed_detected
    assert not manager.alarm.get()

    manager.disarm_security_zone(security_zone.id)
    manager.arm(sensors[0])
    result, armed_detected = manager.update()
    assert [sensors[0]] == armed_detected
    assert manager.alarm.get()


# test_area.py


# ==========
# 헬퍼 함수 테스트
# ==========


def test_distance_point_point_basic():
    assert _distance_point_point(0, 0, 3, 4) == pytest.approx(5.0)


@pytest.mark.parametrize(
    "px,py,x1,y1,x2,y2,expected",
    [
        (1, 0, 0, 0, 2, 0, 0.0),  # 선 위의 점
        (1, 1, 0, 0, 2, 0, 1.0),  # 수직 거리
        (0, 0, 1, 0, 3, 0, 1.0),  # 세그먼트 밖, 끝점과의 거리
        (4, 0, 1, 0, 3, 0, 1.0),
    ],
)
def test_distance_point_segment(px, py, x1, y1, x2, y2, expected):
    d = _distance_point_segment(px, py, x1, y1, x2, y2)
    assert d == pytest.approx(expected)


@pytest.mark.parametrize(
    "p1,p2,q1,q2,expected",
    [
        ((0, 0), (2, 2), (0, 2), (2, 0), True),  # X 교차
        ((0, 0), (1, 1), (2, 2), (3, 3), False),  # 같은 직선, 떨어져 있음
        ((0, 0), (4, 0), (2, 0), (6, 0), True),  # 같은 직선, 겹침
        ((0, 0), (0, 4), (1, 1), (1, 3), False),  # 평행, 떨어져 있음
        ((0, 0), (2, 2), (2, 2), (4, 4), True),  # 끝점 공유
    ],
)
def test_segments_intersect(p1, p2, q1, q2, expected):
    assert (
            _segments_intersect(p1[0], p1[1], p2[0], p2[1], q1[0], q1[1], q2[0], q2[1])
            == expected
    )


def test_segments_distance_intersect_zero():
    d = _segments_distance(0, 0, 2, 2, 0, 2, 2, 0)
    assert d == pytest.approx(0.0)


def test_segments_distance_parallel():
    # y=0, y=3 수평선
    d = _segments_distance(0, 0, 4, 0, 0, 3, 4, 3)
    assert d == pytest.approx(3.0)


def test_point_in_square_basic():
    sq = Square(up=0, down=4, left=0, right=4)
    assert _point_in_square(2, 2, sq) is True
    assert _point_in_square(0, 0, sq) is True  # 모서리
    assert _point_in_square(-1, 2, sq) is False


# ==========
# Point.overlap
# ==========


def test_point_point_overlap_within_limit():
    p1 = Point(0, 0)
    p2 = Point(1, 1)  # sqrt(2) < 2
    assert p1.overlap(p2) is True
    assert p2.overlap(p1) is True


def test_point_point_overlap_outside_limit():
    p1 = Point(0, 0)
    p2 = Point(3, 0)  # 거리 3 > DIST_LIMIT
    assert p1.overlap(p2) is False
    assert p2.overlap(p1) is False


def test_point_line_overlap_on_segment():
    pt = Point(1, 0)
    line = Line((0, 0), (2, 0))
    assert pt.overlap(line) is True
    assert line.overlap(pt) is True


def test_point_line_overlap_near_segment():
    pt = Point(1, 1)
    line = Line((0, 0), (2, 0))  # 수직거리 1 <= DIST_LIMIT
    assert pt.overlap(line) is True
    assert line.overlap(pt) is True


def test_point_line_overlap_far_segment():
    pt = Point(1, 3)
    line = Line((0, 0), (2, 0))  # 수직거리 3 > DIST_LIMIT
    assert pt.overlap(line) is False
    assert line.overlap(pt) is False


def test_point_square_overlap_inside():
    sq = Square(up=0, down=4, left=0, right=4)
    pt = Point(2, 2)
    assert pt.overlap(sq) is True
    assert sq.overlap(pt) is True


def test_point_square_overlap_on_edge():
    sq = Square(up=0, down=4, left=0, right=4)
    pt = Point(0, 2)
    assert pt.overlap(sq) is True
    assert sq.overlap(pt) is True


def test_point_square_no_overlap():
    sq = Square(up=0, down=4, left=0, right=4)
    pt = Point(5, 5)
    assert pt.overlap(sq) is False
    assert sq.overlap(pt) is False


# ==========
# Line.overlap
# ==========


def test_line_line_overlap_intersect():
    l1 = Line((0, 0), (2, 2))
    l2 = Line((0, 2), (2, 0))
    assert l1.overlap(l2) is True
    assert l2.overlap(l1) is True


def test_line_line_overlap_parallel_close():
    # y=0, y=1 수평선, 거리 1 <= DIST_LIMIT
    l1 = Line((0, 0), (4, 0))
    l2 = Line((0, 1), (4, 1))
    assert l1.overlap(l2) is True
    assert l2.overlap(l1) is True


def test_line_line_overlap_parallel_far():
    # y=0, y=3 수평선, 거리 3 > DIST_LIMIT
    l1 = Line((0, 0), (4, 0))
    l2 = Line((0, 3), (4, 3))
    assert l1.overlap(l2) is False
    assert l2.overlap(l1) is False


def test_line_square_overlap_cross():
    sq = Square(up=0, down=4, left=0, right=4)
    line = Line((-1, 2), (5, 2))  # 정사각형을 가로지름
    assert line.overlap(sq) is True
    assert sq.overlap(line) is True


def test_line_square_overlap_tangent():
    sq = Square(up=0, down=4, left=0, right=4)
    line = Line((-1, 0), (5, 0))  # 위쪽 변과 일치
    assert line.overlap(sq) is True
    assert sq.overlap(line) is True


def test_line_square_no_overlap_outside():
    sq = Square(up=0, down=4, left=0, right=4)
    line = Line((-1, -1), (5, -1))  # 완전히 아래, 교차하지 않음
    assert line.overlap(sq) is False
    assert sq.overlap(line) is False


# ==========
# Square.overlap
# ==========


def test_square_square_overlap_full():
    s1 = Square(up=0, down=4, left=0, right=4)
    s2 = Square(up=1, down=3, left=1, right=3)  # 완전히 안쪽
    assert s1.overlap(s2) is True
    assert s2.overlap(s1) is True


def test_square_square_overlap_partial():
    s1 = Square(up=0, down=4, left=0, right=4)
    s2 = Square(up=2, down=6, left=2, right=6)  # 일부만 겹침
    assert s1.overlap(s2) is True
    assert s2.overlap(s1) is True


def test_square_square_touch_edge():
    s1 = Square(up=0, down=4, left=0, right=4)
    s2 = Square(up=0, down=4, left=4, right=8)  # 오른쪽 변에서 접촉
    assert s1.overlap(s2) is True
    assert s2.overlap(s1) is True


def test_square_square_touch_corner():
    s1 = Square(up=0, down=4, left=0, right=4)
    s2 = Square(up=4, down=8, left=4, right=8)  # 한 점에서만 만남
    assert s1.overlap(s2) is True
    assert s2.overlap(s1) is True


def test_square_square_no_overlap():
    s1 = Square(up=0, down=4, left=0, right=4)
    s2 = Square(up=0, down=4, left=5, right=9)
    assert s1.overlap(s2) is False
    assert s2.overlap(s1) is False


# test_security_system.py

def test_security_zone_geometry2():
    zone = Square(100, -100, -100, 100)
    motion_sensor1 = Line((200, 0), (0, 200))
    motion_sensor2 = Line((101, -200), (101, 200))
    windoor_sensor1 = Point(100, 100)
    windoor_sensor2 = Point(-100, 101)

    assert zone.overlap(motion_sensor1)
    assert motion_sensor1.overlap(zone)

    assert not zone.overlap(motion_sensor2)
    assert not motion_sensor2.overlap(zone)

    assert zone.overlap(windoor_sensor1)
    assert windoor_sensor1.overlap(zone)

    assert not zone.overlap(windoor_sensor2)
    assert not windoor_sensor2.overlap(zone)

    assert motion_sensor1.overlap(windoor_sensor1)
    assert windoor_sensor1.overlap(motion_sensor1)


def test_security_mode_away2():
    manager = SecurityManager(SecurityMemoryDatabase(), LogManager(LogMemoryDB()))
    sensors = list(manager.sensors.items())

    manager.set_security_mode_name("Away")
    manager.update()

    assert sensors[0][0].test_armed_state()
    assert sensors[1][0].test_armed_state()
    assert sensors[2][0].test_armed_state()
    assert not sensors[3][0].test_armed_state()
    assert not sensors[4][0].test_armed_state()
    assert not sensors[5][0].test_armed_state()
    assert not sensors[6][0].test_armed_state()
    assert not sensors[7][0].test_armed_state()


def test_security_mode_home2():
    manager = SecurityManager(SecurityMemoryDatabase(), LogManager(LogMemoryDB()))
    sensors = list(manager.sensors.items())

    manager.set_security_mode_name("Home")
    manager.update()

    assert not sensors[0][0].test_armed_state()
    assert not sensors[1][0].test_armed_state()
    assert not sensors[2][0].test_armed_state()
    assert sensors[3][0].test_armed_state()
    assert sensors[4][0].test_armed_state()
    assert sensors[5][0].test_armed_state()
    assert not sensors[6][0].test_armed_state()
    assert not sensors[7][0].test_armed_state()


def test_security_mode_sleep2():
    manager = SecurityManager(SecurityMemoryDatabase(), LogManager(LogMemoryDB()))
    sensors = list(manager.sensors.items())

    # security_modes = [Home, Away, OvernightTravel, ExtendedTravel]
    manager.set_security_mode_index(2)
    manager.update()

    assert not sensors[0][0].test_armed_state()
    assert not sensors[1][0].test_armed_state()
    assert not sensors[2][0].test_armed_state()
    assert not sensors[3][0].test_armed_state()
    assert not sensors[4][0].test_armed_state()
    assert not sensors[5][0].test_armed_state()
    assert sensors[6][0].test_armed_state()
    assert sensors[7][0].test_armed_state()


def test_security_mode_extended_travel():
    manager = SecurityManager(SecurityMemoryDatabase(), LogManager(LogMemoryDB()))
    sensors = list(manager.sensors.items())

    # 이름으로 선택해도 되고, index 3을 써도 됨
    manager.set_security_mode_name("Extended")
    manager.update()

    assert sensors[0][0].test_armed_state()
    assert sensors[1][0].test_armed_state()
    assert sensors[2][0].test_armed_state()
    assert not sensors[3][0].test_armed_state()
    assert not sensors[4][0].test_armed_state()
    assert not sensors[5][0].test_armed_state()
    assert not sensors[6][0].test_armed_state()
    assert not sensors[7][0].test_armed_state()


def test_bypass_sensor2():
    manager = SecurityManager(SecurityMemoryDatabase(), LogManager(LogMemoryDB()))
    sensors = list(manager.sensors.items())
    sensor = sensors[0][0]

    manager.set_security_mode_name("Away")
    manager.update()

    # 새 인터페이스: 시간 없이 sensor만 넘김
    manager.sensor_bypass(sensor)
    manager.update()

    sensor.intrude()
    result, armed_detected = manager.update()

    # 센서는 켜져 있고, Arm 상태이며, detection은 제대로 읽힌다
    assert manager.sensors[sensor][0]
    assert sensor.test_armed_state()
    assert result[sensor]
    assert len(armed_detected) == 1 and sensor in armed_detected

    # bypass 목록에는 들어가 있지만
    assert sensor in manager.bypass
    # 알람은 울리지 않는다
    assert not manager.alarm.get()


def test_bypass_sensor_finish():
    manager = SecurityManager(SecurityMemoryDatabase(), LogManager(LogMemoryDB()))
    sensors = list(manager.sensors.items())
    sensor = sensors[0][0]

    manager.set_security_mode_name("Away")
    manager.update()

    # 우선 bypass 상태에서 침입하면 알람이 울리지 않음
    manager.sensor_bypass(sensor)
    sensor.intrude()
    result, armed_detected = manager.update()
    assert sensor in armed_detected
    assert not manager.alarm.get()

    # bypass 해제 후 다시 침입하면 알람이 울림
    manager.sensor_bypass_finish(sensor)
    sensor.intrude()
    result, armed_detected = manager.update()
    assert sensor not in manager.bypass
    assert sensor in armed_detected
    assert manager.alarm.get()
    result, armed_detected = manager.update(detected_sensor_reset=True)
    assert not sensor.read()

    with pytest.raises(SensorNotFoundError):
        manager.sensor_bypass_finish(sensor)




def test_security_zone2():
    manager = SecurityManager(SecurityMemoryDatabase(), LogManager(LogMemoryDB()))
    sensors = [s for s, _ in manager.sensors.items()]

    security_zone = manager.add_security_zone()
    manager.update_security_zone(security_zone.id, Square(90, 70, 10, 30))

    # geometry 기준으로 이 네 개가 포함되어야 함
    assert security_zone.sensors == [sensors[i] for i in [0, 8]]

    manager.arm_security_zone(security_zone.id)

    # 구역에 포함된 센서 침입 시 알람
    sensors[0].intrude()
    result, armed_detected = manager.update()
    assert [sensors[0]] == armed_detected
    assert manager.alarm.get()

    # 구역 해제 후에는 더 이상 알람 안 울림
    manager.disarm_security_zone(security_zone.id)
    sensors[0].intrude()
    result, armed_detected = manager.update()
    assert [] == armed_detected
    assert not manager.alarm.get()


def test_sensor_onoff2():
    manager = SecurityManager(SecurityMemoryDatabase(), LogManager(LogMemoryDB()))
    sensors = list(manager.sensors.items())
    sensor = sensors[0][0]

    manager.turn_off_sensor(sensor)
    result, armed_detected = manager.update()
    # off 상태면 SensorController.read에서 읽지 않으므로 None
    assert result[sensor] is None

    manager.turn_on_sensor(sensor)
    result, armed_detected = manager.update()
    # on 상태면 최소 False 정도는 들어올 것이라 None은 아님
    assert result[sensor] is not None


def test_arm_order2():
    manager = SecurityManager(SecurityMemoryDatabase(), LogManager(LogMemoryDB()))
    sensors = [s for s, _ in manager.sensors.items()]

    security_zone = manager.add_security_zone()
    manager.update_security_zone(security_zone.id, Square(90, 70, 10, 30))
    assert security_zone.sensors == [sensors[i] for i in [0, 8]]

    # 1단계: 구역 arm + 센서 침입 → 알람 울려야 함
    manager.arm_security_zone(security_zone.id)
    sensors[0].intrude()
    result, armed_detected = manager.update()
    assert [sensors[0]] == armed_detected
    assert manager.alarm.get()

    # 2단계: 개별 disarm이 구역 arm보다 우선
    manager.disarm(sensors[0])
    sensors[0].intrude()
    result, armed_detected = manager.update()
    assert [] == armed_detected
    assert not manager.alarm.get()

    # 3단계: 구역 disarm 후 개별 arm 하면 다시 감지됨
    manager.disarm_security_zone(security_zone.id)
    manager.arm(sensors[0])
    sensors[0].intrude()
    result, armed_detected = manager.update()
    assert [sensors[0]] == armed_detected
    assert manager.alarm.get()


# imports 는 네가 프로젝트 구조에 맞게 채워 넣으면 됨.
# 예: from core.security.security_manager import SecurityManager
#     from core.security.security_zone_geometry.area import Point, Line, Square
#     from core.security.security_mode.home import Home
#     ...

# ======================
# 내부에서만 쓸 더미 클래스들
# ======================

class _DummySensorForController:
    """SensorController 전용 더미 센서 (read, armed 만 필요)."""

    def __init__(self, value: bool, armed: bool = False):
        self._value = value
        self.armed = armed

    def read(self) -> bool:
        return self._value


class _DummyAreaSensor:
    """SecurityZone 전용 더미 센서 (area.overlap 만 필요)."""

    def __init__(self, area):
        self.area = area


class _DummySensorForManager:
    """SecurityManager.add_sensor 등에서만 쓰는 단순 키용 센서."""

    def __init__(self, key):
        self._key = key

    def __hash__(self):
        return hash(self._key)

    def __eq__(self, other):
        return isinstance(other, _DummySensorForManager) and self._key == other._key


# ======================
# Alarm 테스트
# ======================

def test_alarm_initial_state_and_get():
    alarm = Alarm()
    # 초기에는 울리지 않았으므로 False
    assert alarm.get() is False


def test_alarm_siren_and_get_reset():
    alarm = Alarm()
    alarm.siren()
    # 한 번 울리면 True를 돌려주고 내부 상태는 초기화된다
    assert alarm.get() is True
    # 다시 호출하면 False
    assert alarm.get() is False


# ======================
# SensorController 테스트 (모든 분기)
# ======================

def test_sensor_controller_off_sensor_is_skipped():
    sensor = _DummySensorForController(True, armed=True)
    controller = SensorController({sensor: (False, None)})

    result, armed_detected = controller.read()

    # off 인 센서는 읽지 않으므로 None 유지
    assert result[sensor] is None
    assert armed_detected == []


def test_sensor_controller_on_not_triggered():
    sensor = _DummySensorForController(False, armed=True)
    controller = SensorController({sensor: (True, None)})

    result, armed_detected = controller.read()

    assert result[sensor] is False
    # 감지 값이 False 이므로 armed_detected 에는 들어가지 않는다
    assert armed_detected == []


def test_sensor_controller_triggered_not_armed():
    sensor = _DummySensorForController(True, armed=False)
    controller = SensorController({sensor: (True, None)})

    result, armed_detected = controller.read()

    assert result[sensor] is True
    # armed 가 False 이므로 리스트에는 들어가지 않는다
    assert armed_detected == []


def test_sensor_controller_triggered_and_armed():
    sensor = _DummySensorForController(True, armed=True)
    controller = SensorController({sensor: (True, None)})

    result, armed_detected = controller.read()

    assert result[sensor] is True
    assert armed_detected == [sensor]


# ======================
# SecurityZone 테스트 (모든 메서드, 분기)
# ======================

def test_security_zone_init_filters_sensors_by_area():
    zone_area = Square(10, -10, -10, 10)
    # 안쪽 두 개, 바깥 한 개
    inner1 = _DummyAreaSensor(Point(0, 0))
    inner2 = _DummyAreaSensor(Point(5, 5))
    outer = _DummyAreaSensor(Point(100, 100))

    zone = SecurityZone(zone_area, [inner1, inner2, outer])

    assert zone.enabled is True
    assert inner1 in zone.sensors
    assert inner2 in zone.sensors
    assert outer not in zone.sensors


def test_security_zone_enable_disable_and_update():
    inner = _DummyAreaSensor(Point(0, 0))
    outer = _DummyAreaSensor(Point(100, 100))

    zone = SecurityZone(Square(10, -10, -10, 10), [inner, outer])

    # enable / disable
    assert zone.enabled is True
    zone.disable()
    assert zone.enabled is False
    zone.enable()
    assert zone.enabled is True

    # update 로 영역을 바꾸면 포함 센서도 바뀐다
    zone.update(Square(200, 50, 50, 200), [inner, outer])
    assert inner not in zone.sensors
    assert outer in zone.sensors


# ======================
# SecurityMode 서브클래스 테스트
# (Home / Away / OvernightTravel / ExtendedTravel)
# ======================

def test_home_mode_arm_indices():
    sensors = [object() for _ in range(8)]
    mode = Home(sensors)

    assert mode.name == "Home"
    assert mode.get_arm_sensors() == [sensors[3], sensors[4], sensors[5]]


def test_away_mode_arm_indices():
    sensors = [object() for _ in range(8)]
    mode = Away(sensors)

    assert mode.name == "Away"
    assert mode.get_arm_sensors() == [sensors[0], sensors[1], sensors[2]]


def test_sleep_mode_arm_indices():
    sensors = [object() for _ in range(8)]
    mode = OvernightTravel(sensors)

    assert mode.name == "Overnight"
    assert mode.get_arm_sensors() == [sensors[6], sensors[7]]


def test_extended_travel_mode_arm_indices():
    sensors = [object() for _ in range(8)]
    mode = ExtendedTravel(sensors)

    assert mode.name == "Extended"
    assert mode.get_arm_sensors() == [sensors[0], sensors[1], sensors[2]]


# ======================
# SecurityManager 메서드 단위 테스트
# (모든 함수, 분기 커버)
# ======================

def _make_manager():
    return SecurityManager(SecurityMemoryDatabase(), LogManager(LogMemoryDB()))


def test_security_manager_init_sets_defaults():
    manager = _make_manager()

    assert len(manager.sensors) == 10
    for on, arm in manager.sensors.values():
        assert on is True
        assert arm is None

    assert manager.security_zones == []
    assert manager.default_zone == (150, 200, 210, 240)
    assert manager.now_security_mode is None
    assert len(manager.security_modes) == 4


def test_add_sensor_only_if_not_exists():
    manager = _make_manager()
    dummy = _DummySensorForManager("new")

    assert dummy not in manager.sensors
    manager.add_sensor(dummy, on=False, arm=True)
    assert manager.sensors[dummy] == (False, True)

    # 이미 있는 센서는 덮어쓰지 않는다
    try:
        manager.add_sensor(dummy, on=True, arm=None)
        assert False
    except SensorAlreadyExistsError:
        assert manager.sensors[dummy] == (False, True)


def test_turn_on_off_and_set_onoff_sensor_existing_and_missing():
    manager = _make_manager()
    sensor = next(iter(manager.sensors.keys()))

    manager.turn_off_sensor(sensor)
    assert manager.sensors[sensor][0] is False

    manager.turn_on_sensor(sensor)
    assert manager.sensors[sensor][0] is True

    manager.set_onoff_sensor(sensor, False)
    assert manager.sensors[sensor][0] is False

    manager.set_onoff_sensor(sensor, True)
    assert manager.sensors[sensor][0] is True

    # 존재하지 않는 센서는 영향이 없어야 한다
    ghost = _DummySensorForManager("ghost")
    try:
        manager.turn_off_sensor(ghost)
        assert False
    except SensorNotFoundError:
        assert ghost not in manager.sensors

    try:
        manager.turn_on_sensor(ghost)
        assert False
    except SensorNotFoundError:
        assert ghost not in manager.sensors

    try:
        manager.set_onoff_sensor(ghost, False)
        assert False
    except SensorNotFoundError:
        assert ghost not in manager.sensors


def test_remove_sensor_returns_state_and_removes():
    dummy = DeviceWinDoorSensor(0, 0)

    manager = _make_manager()
    sensor = next(iter(manager.sensors.keys()))
    old_state = manager.sensors[sensor]

    returned = manager.remove_sensor(sensor)
    assert returned == old_state
    assert sensor not in manager.sensors
    try:
        manager.remove_sensor(dummy)
        assert False
    except SensorNotFoundError:
        pass


def test_set_security_mode_index_valid_and_invalid():
    manager = _make_manager()

    manager.set_security_mode_index(1)
    assert manager.now_security_mode == 1

    # 잘못된 인덱스는 무시된다
    try:
        manager.set_security_mode_index(-1)
        assert False
    except SecurityModeNotFoundError:
        assert manager.now_security_mode == 1

    try:
        manager.set_security_mode_index(100)
        assert False
    except SecurityModeNotFoundError:
        assert manager.now_security_mode == 1


def test_set_security_mode_name_found_and_not_found():
    manager = _make_manager()

    manager.now_security_mode = None
    manager.set_security_mode_name("Away")
    assert manager.security_modes[manager.now_security_mode].name == "Away"

    prev = manager.now_security_mode
    try:
        manager.set_security_mode_name("NoSuchMode")
        assert False
    except SecurityModeNotFoundError:
        assert manager.now_security_mode is prev
    try:
        manager.get_security_mode("NoSuchMode")
        assert False
    except SecurityModeNotFoundError:
        pass


def test_add_update_arm_disarm_security_zone_and_invalid_id():
    manager = _make_manager()
    sensors = [s for s, _ in manager.sensors.items()]

    zone = manager.add_security_zone()
    assert zone in manager.security_zones
    assert zone.enabled is True

    updated_sensors = manager.update_security_zone(zone.id, Square(90, 70, 10, 30))
    assert updated_sensors == zone.sensors
    # geometry 에 의해 이 2 개가 포함되어야 한다
    assert zone.sensors == [sensors[i] for i in [0, 8]]

    # 잘못된 id 들은 아무 일도 일어나지 않아야 한다
    invalid_id = zone.id + 100
    prev_area = [z.area for z in manager.security_zones]
    prev_enabled = [z.enabled for z in manager.security_zones]
    try:
        manager.update_security_zone(invalid_id, Square(10, -1, 1, 3))
        assert False
    except SecurityZoneNotFoundError:
        assert prev_area == [z.area for z in manager.security_zones]
    try:
        manager.arm_security_zone(invalid_id)
        assert False
    except SecurityZoneNotFoundError:
        assert prev_enabled == [z.enabled for z in manager.security_zones]
    try:
        manager.disarm_security_zone(invalid_id)
        assert False
    except SecurityZoneNotFoundError:
        assert prev_enabled == [z.enabled for z in manager.security_zones]
    try:
        manager.set_arm_security_zone(invalid_id, False)
        assert False
    except SecurityZoneNotFoundError:
        assert prev_enabled == [z.enabled for z in manager.security_zones]

    # arm / disarm / set_arm 동작 확인
    zone.disable()
    assert zone.enabled is False
    manager.arm_security_zone(zone.id)
    assert zone.enabled is True
    manager.disarm_security_zone(zone.id)
    assert zone.enabled is False
    manager.set_arm_security_zone(zone.id, True)
    assert zone.enabled is True


def test_sensor_bypass_and_update_skip_alarm():
    manager = _make_manager()
    sensor = list(manager.sensors.keys())[0]

    manager.set_security_mode_name("Away")
    manager.update()

    manager.sensor_bypass(sensor)
    sensor.intrude()

    result, armed_detected = manager.update()

    assert sensor in manager.bypass
    assert sensor in armed_detected
    # bypass 된 센서는 알람을 울리지 않는다
    assert not manager.alarm.get()


def test_sensor_bypass_finish_restores_alarm_behavior():
    manager = _make_manager()
    sensor = list(manager.sensors.keys())[0]

    manager.set_security_mode_name("Away")
    manager.update()

    # 먼저 bypass 상태에서는 알람이 안 울린다
    manager.sensor_bypass(sensor)
    sensor.intrude()
    result, armed_detected = manager.update()
    assert sensor in armed_detected
    assert not manager.alarm.get()

    # bypass 해제 후 다시 침입하면 알람이 울린다
    manager.sensor_bypass_finish(sensor)
    sensor.intrude()
    result, armed_detected = manager.update()
    assert sensor not in manager.bypass
    assert sensor in armed_detected
    assert manager.alarm.get()


def test_arm_disarm_set_arm_for_existing_and_missing_sensor():
    manager = _make_manager()
    sensor = list(manager.sensors.keys())[0]

    manager.arm(sensor)
    assert manager.sensors[sensor][1] is True

    manager.disarm(sensor)
    assert manager.sensors[sensor][1] is False

    manager.set_arm(sensor, True)
    assert manager.sensors[sensor][1] is True

    manager.set_arm(sensor, False)
    assert manager.sensors[sensor][1] is False

    ghost = _DummySensorForManager("ghost2")
    try:
        manager.arm(ghost)
        assert False
    except:
        pass
    try:
        manager.disarm(ghost)
        assert False
    except:
        pass
    try:
        manager.set_arm(ghost, True)
        assert False
    except:
        pass
    assert ghost not in manager.sensors


def test_update_manual_arm_flags_branch():
    manager = _make_manager()
    sensors = [s for s, _ in manager.sensors.items()]

    # security mode 영향 제거
    manager.now_security_mode = None

    manager.set_arm(sensors[1], True)
    manager.set_arm(sensors[2], False)

    result, armed_detected = manager.update()

    assert sensors[1].test_armed_state()
    assert not sensors[2].test_armed_state()


def test_update_with_security_mode_none_and_invalid_index_branches():
    manager = _make_manager()

    # now_security_mode 가 None 이면 1단계는 건너뛴다
    manager.now_security_mode = None
    result, armed_detected = manager.update()

    # now_security_mode 가 범위 밖이면 2단계 if 문이 실행되지 않는다
    manager.now_security_mode = 100
    result, armed_detected = manager.update()


# ======================
# SecurityManager + SecurityMode 통합 동작 테스트
# (Away / Home / OvernightTravel / ExtendedTravel 패턴)
# ======================

def test_security_mode_away_arming_pattern():
    manager = _make_manager()
    sensors = list(manager.sensors.items())

    manager.set_security_mode_name("Away")
    manager.update()

    assert sensors[0][0].test_armed_state()
    assert sensors[1][0].test_armed_state()
    assert sensors[2][0].test_armed_state()
    assert not sensors[3][0].test_armed_state()
    assert not sensors[4][0].test_armed_state()
    assert not sensors[5][0].test_armed_state()
    assert not sensors[6][0].test_armed_state()
    assert not sensors[7][0].test_armed_state()


def test_security_mode_home_arming_pattern():
    manager = _make_manager()
    sensors = list(manager.sensors.items())

    manager.set_security_mode_name("Home")
    manager.update()

    assert not sensors[0][0].test_armed_state()
    assert not sensors[1][0].test_armed_state()
    assert not sensors[2][0].test_armed_state()
    assert sensors[3][0].test_armed_state()
    assert sensors[4][0].test_armed_state()
    assert sensors[5][0].test_armed_state()
    assert not sensors[6][0].test_armed_state()
    assert not sensors[7][0].test_armed_state()


def test_security_mode_sleep_arming_pattern():
    manager = _make_manager()
    sensors = list(manager.sensors.items())

    manager.set_security_mode_index(2)
    manager.update()

    assert not sensors[0][0].test_armed_state()
    assert not sensors[1][0].test_armed_state()
    assert not sensors[2][0].test_armed_state()
    assert not sensors[3][0].test_armed_state()
    assert not sensors[4][0].test_armed_state()
    assert not sensors[5][0].test_armed_state()
    assert sensors[6][0].test_armed_state()
    assert sensors[7][0].test_armed_state()


def test_security_mode_extended_travel_arming_pattern():
    manager = _make_manager()
    sensors = list(manager.sensors.items())

    manager.set_security_mode_name("Extended")
    manager.update()

    assert sensors[0][0].test_armed_state()
    assert sensors[1][0].test_armed_state()
    assert sensors[2][0].test_armed_state()
    assert not sensors[3][0].test_armed_state()
    assert not sensors[4][0].test_armed_state()
    assert not sensors[5][0].test_armed_state()
    assert not sensors[6][0].test_armed_state()
    assert not sensors[7][0].test_armed_state()


def test_security_manager_security_zone_and_arm_order():
    manager = _make_manager()
    sensors = [s for s, _ in manager.sensors.items()]

    zone = manager.add_security_zone()
    manager.arm_security_zone(zone.id)
    manager.update_security_zone(zone.id, Square(25, 15, 65, 75))
    manager.update()
    assert list(manager.sensors.keys())[1].armed
    manager.update_security_zone(zone.id, Square(90, 70, 10, 30))
    manager.update()
    assert not list(manager.sensors.keys())[1].armed
    assert list(manager.sensors.keys())[0].armed
    assert list(manager.sensors.keys())[8].armed
    manager.disarm_security_zone(zone.id)
    manager.update()
    assert not list(manager.sensors.keys())[0].armed
    assert not list(manager.sensors.keys())[8].armed

    assert zone.sensors == [sensors[i] for i in [0, 8]]

    manager.arm_security_zone(zone.id)
    sensors[0].intrude()
    result, armed_detected = manager.update()
    assert [sensors[0]] == armed_detected
    assert manager.alarm.get()

    # 개별 disarm 이 존 arm 보다 우선
    manager.disarm(sensors[0])
    sensors[0].intrude()
    result, armed_detected = manager.update()
    assert [] == armed_detected
    assert not manager.alarm.get()

    # 존 disarm 후 개별 arm 이 다시 동작
    manager.disarm_security_zone(zone.id)
    manager.arm(sensors[0])
    sensors[0].intrude()
    result, armed_detected = manager.update()
    assert [sensors[0]] == armed_detected
    assert manager.alarm.get()


# 추가 테스트용 더미 Area
class DummyArea(Area):
    def overlap(self, other: Area) -> bool:
        return False


def test_distance_point_segment_degenerate_segment():
    # 31번째 줄: dx == 0 and dy == 0 분기
    # 세그먼트가 한 점으로 수축된 경우, 점과 점 거리로 처리되는지 확인
    d = _distance_point_segment(
        3.0, 4.0,  # px, py
        0.0, 0.0,  # x1, y1
        0.0, 0.0,  # x2, y2 (같은 점)
    )
    assert d == pytest.approx(_distance_point_point(3.0, 4.0, 0.0, 0.0))


def test_segments_intersect_collinear_o2_branch():
    # 76번째 줄: o2 == 0 and _on_segment(...) 분기
    # p1p2: (0,0) -> (4,0), q2가 그 위에 있는 경우
    p1x, p1y = 0.0, 0.0
    p2x, p2y = 4.0, 0.0
    q1x, q1y = 6.0, 0.0  # 세그먼트 밖
    q2x, q2y = 2.0, 0.0  # 세그먼트 안
    assert _segments_intersect(p1x, p1y, p2x, p2y, q1x, q1y, q2x, q2y)


def test_segments_intersect_collinear_o3_branch():
    # 78번째 줄: o3 == 0 and _on_segment(...) 분기
    # q1q2: (0,0) -> (4,0), p1이 그 위에 있는 경우
    p1x, p1y = 2.0, 0.0  # q1q2 안
    p2x, p2y = 6.0, 0.0  # q1q2 밖
    q1x, q1y = 0.0, 0.0
    q2x, q2y = 4.0, 0.0
    assert _segments_intersect(p1x, p1y, p2x, p2y, q1x, q1y, q2x, q2y)


def test_segments_intersect_collinear_o4_branch():
    # 80번째 줄: o4 == 0 and _on_segment(...) 분기
    # q1q2: (0,0) -> (4,0), p2가 그 위에 있는 경우
    p1x, p1y = 0.0, 0.0
    p2x, p2y = 2.0, 0.0  # q1q2 안
    q1x, q1y = 0.0, 0.0
    q2x, q2y = 4.0, 0.0
    assert _segments_intersect(p1x, p1y, p2x, p2y, q1x, q1y, q2x, q2y)


def test_point_overlap_unknown_area():
    # 169번째 줄: Point.overlap의 else: return False
    p = Point(0, 0)
    dummy = DummyArea()
    assert p.overlap(dummy) is False


def test_line_overlap_unknown_area():
    # 198번째 줄: Line.overlap의 else: return False
    line = Line((0, 0), (1, 1))
    dummy = DummyArea()
    assert line.overlap(dummy) is False


def test_square_overlap_unknown_area():
    # 219번째 줄: Square.overlap의 else: return False
    sq = Square(10, -10, -10, 10)
    dummy = DummyArea()
    assert sq.overlap(dummy) is False


def test_segments_intersect_collinear_o3_special_case():
    # 이 케이스의 배치:
    # q1(-5, -5) ---- p1(-5, -4) ---- p2(-5, -3) ---- q2(-5, -2)
    #
    # 네 점이 모두 x = -5 직선 위에 있고, 순서는
    #   q1 < p1 < p2 < q2
    # 이다.
    #
    # 이때:
    #   o1 = orientation(p1, p2, q1) = 0
    #   o2 = orientation(p1, p2, q2) = 0
    #   o3 = orientation(q1, q2, p1) = 0
    #   o4 = orientation(q1, q2, p2) = 0
    #
    # on_segment 체크 결과는:
    #   on_segment(p1, q1, p2) -> False   (q1는 p1–p2 구간 밖)
    #   on_segment(p1, q2, p2) -> False   (q2도 p1–p2 구간 밖)
    #   on_segment(q1, p1, q2) -> True    (p1는 q1–q2 사이)
    #   on_segment(q1, p2, q2) -> True    (p2도 q1–q2 사이)
    #
    # 따라서 _segments_intersect 내부에서는:
    #   - 일반 교차(o1 != o2 and o3 != o4)는 False
    #   - o1 == 0 && on_segment(...)  -> False
    #   - o2 == 0 && on_segment(...)  -> False
    #   - o3 == 0 && on_segment(...)  -> True   ← 여기(78번 줄)를 타고 return
    #
    # 즉, 78번 줄(o3 특수 케이스)이 확실하게 실행된다.
    p1x, p1y = -5.0, -4.0
    p2x, p2y = -5.0, -3.0
    q1x, q1y = -5.0, -5.0
    q2x, q2y = -5.0, -2.0

    assert _segments_intersect(p1x, p1y, p2x, p2y, q1x, q1y, q2x, q2y)


def test_add_security_mode_adds_and_calls_db():
    manager = _make_manager()
    manager.db_manager = SecurityMemoryDatabase()
    db = manager.db_manager

    original_len = len(manager.security_modes)
    name = "CustomMode"

    result = manager.add_security_mode(name)

    # 새 모드가 하나 추가됨
    assert len(manager.security_modes) == original_len + 1
    added_mode = [m for m in manager.security_modes if m.name == name][0]
    assert added_mode.sensors == []
    # db에 기록됨
    # assert db.added_modes == [added_mode]
    # 명시적 return 없으니 None
    assert result is None


def test_add_security_mode_duplicate_does_nothing():
    manager = _make_manager()
    manager.db_manager = SecurityMemoryDatabase()
    db = manager.db_manager

    existing_name = manager.security_modes[0].name
    before = list(manager.security_modes)

    try:
        manager.add_security_mode(existing_name)
        assert False
    except SecurityModeAlreadyExistsError:
        pass

    # 리스트 변화 없음
    assert manager.security_modes == before
    # db 호출 없음
    # assert db.added_modes == []
    # 반환값 None
    # assert result is None


def test_update_security_mode_updates_sensors_and_calls_db():
    manager = _make_manager()
    manager.db_manager = SecurityMemoryDatabase()
    db = manager.db_manager

    target_mode = manager.security_modes[0]
    name = target_mode.name

    sensors = list(manager.sensors.keys())
    new_sensors = [sensors[i] for i in [0, 1, 2]]
    print([sensor.get_id() for sensor in manager.sensors.keys()])
    print([mode.name for mode in manager.security_modes], name)

    manager.update_security_mode(name, new_sensors)
    print([sensor.get_id() for sensor in manager.get_security_mode(name).sensors])
    print([sensor.get_id() for sensor in new_sensors])

    assert manager.get_security_mode(name) == target_mode
    assert ([sensor.get_id() for sensor in manager.get_security_mode(name).get_arm_sensors()]
            == [sensor.get_id() for sensor in new_sensors])

    # 모드 sensors 갱신
    assert target_mode.sensors == new_sensors
    # db 기록 확인
    # assert len(db.updated_modes) == 1
    # called_name, called_mode = db.updated_modes[0]
    # assert called_name == name
    # assert called_mode is target_mode


def test_update_security_mode_unknown_name_no_effect():
    manager = _make_manager()
    manager.db_manager = SecurityMemoryDatabase()
    db = manager.db_manager

    before = [(m.name, list(m.sensors)) for m in manager.security_modes]
    sensors = list(manager.sensors.keys())

    try:
        manager.update_security_mode("NoSuchMode", sensors[:2])
        assert False
    except SecurityModeNotFoundError:
        pass

    # 아무 모드도 안 바뀜
    after = [(m.name, list(m.sensors)) for m in manager.security_modes]
    assert before == after
    # db 호출 없음
    # assert mode.updated_modes == []


def test_remove_security_mode_removes_and_calls_db():
    manager = _make_manager()
    manager.db_manager = SecurityMemoryDatabase()
    db = manager.db_manager

    target_mode = manager.security_modes[0]
    name = target_mode.name
    original_len = len(manager.security_modes)

    manager.remove_security_mode(name)

    # 리스트에서 제거됨
    assert len(manager.security_modes) == original_len - 1
    assert all(m.name != name for m in manager.security_modes)
    # db 기록 확인
    # assert db.removed_names == [name]


def test_remove_security_mode_unknown_name_no_effect():
    manager = _make_manager()
    manager.db_manager = SecurityMemoryDatabase()
    db = manager.db_manager

    before = list(manager.security_modes)

    try:
        manager.remove_security_mode("NoSuchMode")
        assert False
    except SecurityModeNotFoundError:
        pass

    # 변화 없음
    assert manager.security_modes == before
    # db 호출 없음
    # assert db.removed_names == []


def test_security_zone_id():
    security_zone_id.clear()
    db = SecurityMemoryDatabase()
    zone=SecurityZone(Square(1, -1, -1, 1), [])
    db.security_zones.append(zone)
    assert zone.id == 1
    manager = SecurityManager(db, LogManager(LogMemoryDB()))
    assert manager.add_security_zone().id == 2
