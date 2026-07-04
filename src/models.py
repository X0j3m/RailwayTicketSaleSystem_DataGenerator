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
    id: str | None = None
    start_station: str | None = None
    end_station: str | None = None
    start_station_code: str | None = None
    end_station_code: str | None = None
    route: list[str] | None = []
    distance: int | None = None


class TrainTypeModel(BaseModel):
    id: str | None = None
    type: str | None = None
    velocity: int | None = None


class TrainModel(BaseModel):
    id: str | None = None
    type: str | None = None
    number: int | None = None
    velocity: int | None = None


class CarModel(BaseModel):
    id: str | None = None


class SeatModel(BaseModel):
    id: str | None = None
    car_id: str | None = None
    number: int | None = None
    x_pos: int | None = None
    y_pos: int | None = None


class TrainCompositionModel(BaseModel):
    id: str | None = None
    train_id: str | None = None


class TrainCompositionCarModel(BaseModel):
    composition_id: str | None = None
    car_id: str | None = None
    car_number: int | None = None


class StopModel(BaseModel):
    id: str | None = None
    start_station_time: str | None = None
    arrival_time_minutes: int | None = None
    departure_time_minutes: int | None = None
    station_id: str | None = None

class LeadsToRelationModel(BaseModel):
    id: str | None = None
    from_stop_id: str | None = None
    to_stop_id: str | None = None
    duration: int | None = None

class TransferRelationModel(BaseModel):
    id: str | None = None
    from_stop_id: str | None = None
    to_stop_id: str | None = None
    waiting_time: int | None = None