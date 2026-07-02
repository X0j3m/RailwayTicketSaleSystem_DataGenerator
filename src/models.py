from pydantic import BaseModel

class ConnectionModel(BaseModel):
    id: str | None = None
    source_id: str | None = None
    source_name: str | None = None
    target_id: str | None = None
    target_name: str | None = None
    distance: int | None = None


class StationModel(BaseModel):
    id: str | None = None
    city: str | None = None
    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None

class RouteModel(BaseModel):
    start_station_code: str | None = None
    end_station_code: str | None = None
    route: list[str] | None = []