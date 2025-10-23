from math import cos, radians

from app.schemas.utils import BoundingBox


def get_bounding_box_area(
    latitude: float,
    longitude: float,
    radius_km: float,
) -> BoundingBox:
    """
    Высчитывает координаты ограничивающего прямоугольника для круга с заданным радиусом.
    Возвращает BoundingBox.
    """
    if radius_km <= 0:
        raise ValueError("Radius must be > 0")

    lat_delta = radius_km / 111
    lon_delta = radius_km / (111 * cos(radians(latitude)))

    box = BoundingBox(
        min_lon=longitude - lon_delta,
        min_lat=latitude - lat_delta,
        max_lon=longitude + lon_delta,
        max_lat=latitude + lat_delta,
    )
    return box