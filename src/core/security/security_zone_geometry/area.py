from __future__ import annotations

from abc import ABC, abstractmethod
from math import hypot
from typing import Tuple


Coordinate = Tuple[int, int]
Number = float  # 거리 계산용


DIST_LIMIT: float = 2.0  # 거리 2 이하면 겹친다고 판단


def _distance_point_point(x1: Number, y1: Number, x2: Number, y2: Number) -> float:
    return hypot(x1 - x2, y1 - y2)


def _distance_point_segment(
    px: Number,
    py: Number,
    x1: Number,
    y1: Number,
    x2: Number,
    y2: Number,
) -> float:
    dx: float = x2 - x1
    dy: float = y2 - y1

    if dx == 0 and dy == 0:
        return _distance_point_point(px, py, x1, y1)

    t: float = ((px - x1) * dx + (py - y1) * dy) / float(dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    cx: float = x1 + t * dx
    cy: float = y1 + t * dy
    return _distance_point_point(px, py, cx, cy)


def _orientation(ax: Number, ay: Number, bx: Number, by: Number, cx: Number, cy: Number) -> int:
    val: float = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
    if val > 0:
        return 1
    if val < 0:
        return -1
    return 0


def _on_segment(px: Number, py: Number, qx: Number, qy: Number, rx: Number, ry: Number) -> bool:
    return min(px, rx) <= qx <= max(px, rx) and min(py, ry) <= qy <= max(py, ry)


def _segments_intersect(
    p1x: Number,
    p1y: Number,
    p2x: Number,
    p2y: Number,
    q1x: Number,
    q1y: Number,
    q2x: Number,
    q2y: Number,
) -> bool:
    o1: int = _orientation(p1x, p1y, p2x, p2y, q1x, q1y)
    o2: int = _orientation(p1x, p1y, p2x, p2y, q2x, q2y)
    o3: int = _orientation(q1x, q1y, q2x, q2y, p1x, p1y)
    o4: int = _orientation(q1x, q1y, q2x, q2y, p2x, p2y)

    # 일반 교차
    if o1 != o2 and o3 != o4:
        return True

    # 특수 케이스: 일직선 위에 있을 때
    if o1 == 0 and _on_segment(p1x, p1y, q1x, q1y, p2x, p2y):
        return True
    if o2 == 0 and _on_segment(p1x, p1y, q2x, q2y, p2x, p2y):
        return True
    if o3 == 0 and _on_segment(q1x, q1y, p1x, p1y, q2x, q2y):
        return True

    return False


def _segments_distance(
    a1x: Number,
    a1y: Number,
    a2x: Number,
    a2y: Number,
    b1x: Number,
    b1y: Number,
    b2x: Number,
    b2y: Number,
) -> float:
    if _segments_intersect(a1x, a1y, a2x, a2y, b1x, b1y, b2x, b2y):
        return 0.0

    d1: float = _distance_point_segment(a1x, a1y, b1x, b1y, b2x, b2y)
    d2: float = _distance_point_segment(a2x, a2y, b1x, b1y, b2x, b2y)
    d3: float = _distance_point_segment(b1x, b1y, a1x, a1y, a2x, a2y)
    d4: float = _distance_point_segment(b2x, b2y, a1x, a1y, a2x, a2y)
    return min(d1, d2, d3, d4)


def _rect_bounds(square: Square) -> Tuple[int, int, int, int]:
    x1, y_up = square.up_left
    x2, y_down = square.down_right
    left: int = min(x1, x2)
    right: int = max(x1, x2)
    down: int = min(y_up, y_down)
    up: int = max(y_up, y_down)
    return left, down, right, up


def _point_in_square(px: Number, py: Number, square: Square) -> bool:
    left, down, right, up = _rect_bounds(square)
    return left <= px <= right and down <= py <= up


def _line_square_intersect(line: Line, square: Square) -> bool:
    x1, y1 = line.start
    x2, y2 = line.end

    # 끝점이 안에 있으면 겹침
    if _point_in_square(x1, y1, square) or _point_in_square(x2, y2, square):
        return True

    left, down, right, up = _rect_bounds(square)

    edges: Tuple[Tuple[Number, Number, Number, Number], ...] = (
        (left, down, left, up),    # 왼쪽 변
        (right, down, right, up),  # 오른쪽 변
        (left, up, right, up),     # 위쪽 변
        (left, down, right, down)  # 아래쪽 변
    )

    for ex1, ey1, ex2, ey2 in edges:
        if _segments_intersect(x1, y1, x2, y2, ex1, ey1, ex2, ey2):
            return True

    return False


class Area(ABC):
    @abstractmethod
    def overlap(self, other: Area) -> bool:
        ...


class Point(Area):
    x: int
    y: int

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def overlap(self, other: Area) -> bool:
        if isinstance(other, Point):
            return _distance_point_point(self.x, self.y, other.x, other.y) <= DIST_LIMIT
        elif isinstance(other, Line):
            x1, y1 = other.start
            x2, y2 = other.end
            d: float = _distance_point_segment(self.x, self.y, x1, y1, x2, y2)
            return d <= DIST_LIMIT
        elif isinstance(other, Square):
            return _point_in_square(self.x, self.y, other)
        else:
            return False


class Line(Area):
    start: Coordinate
    end: Coordinate

    def __init__(self, start: Coordinate, end: Coordinate) -> None:
        self.start = start
        self.end = end

    def overlap(self, other: Area) -> bool:
        if isinstance(other, Point):
            px: int = other.x
            py: int = other.y
            x1, y1 = self.start
            x2, y2 = self.end
            d: float = _distance_point_segment(px, py, x1, y1, x2, y2)
            return d <= DIST_LIMIT
        elif isinstance(other, Line):
            x1, y1 = self.start
            x2, y2 = self.end
            x3, y3 = other.start
            x4, y4 = other.end
            d: float = _segments_distance(x1, y1, x2, y2, x3, y3, x4, y4)
            return d <= DIST_LIMIT
        elif isinstance(other, Square):
            return _line_square_intersect(self, other)
        else:
            return False


class Square(Area):
    up_left: Coordinate
    down_right: Coordinate

    def __init__(self, up: int, down: int, left: int, right: int) -> None:
        self.up_left = (left, up)
        self.down_right = (right, down)

    def overlap(self, other: Area) -> bool:
        if isinstance(other, Point):
            return _point_in_square(other.x, other.y, self)
        elif isinstance(other, Line):
            return _line_square_intersect(other, self)
        elif isinstance(other, Square):
            left1, down1, right1, up1 = _rect_bounds(self)
            left2, down2, right2, up2 = _rect_bounds(other)
            return not (right1 < left2 or right2 < left1 or up1 < down2 or up2 < down1)
        else:
            return False
