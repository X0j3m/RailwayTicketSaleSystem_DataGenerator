import random

from json_handler import *
from models import *
import uuid

import paths_creator

RES_PATH = "../../res"

trains_types_dict = open_json_file("train_types")
train_types = [TrainTypeModel(**item) for item in trains_types_dict]

routes_dict = open_json_file("train_routes")
routes = [RouteModel(**item) for item in routes_dict]

train_codes = [i for i in range(1000, 10000)]

trains = []
cars = []
seats = []
compositions = []
compositions_cars = []


def generate_composition():
    composition_id = str(uuid.uuid4())

    train = generate_train()
    trains.append(train.__dict__)

    composition = TrainCompositionModel(
        id=composition_id,
        train_id=train.id,
    )

    cars_num = random.randrange(7, 15)

    for i in range(cars_num):
        car, generated_seats = generate_car()
        car_num = i + 1
        cars.append(car.__dict__)
        train_composition_car = TrainCompositionCarModel(
            composition_id=composition_id,
            car_id=car.id,
            car_number=car_num
        )
        compositions_cars.append(train_composition_car.__dict__)
        for seat in generated_seats:
            seats.append(seat.__dict__)

    return composition


def generate_train():
    train_id = str(uuid.uuid4())
    train_type = random.choice(train_types)
    train_code = train_codes.pop(random.randrange(len(train_codes)))

    train = TrainModel(
        id=train_id,
        type=train_type.type,
        number=train_code,
        velocity=train_type.velocity,
    )

    return train


def generate_car():
    car_id = str(uuid.uuid4())

    car = CarModel(id=car_id)

    seats_cols = 4
    seats_rows = random.randrange(14, 20, step=2)

    car_seats = []
    seat_num = 1
    for i in range(seats_rows):
        for j in range(seats_cols):
            seat = generate_seat(car_id, seat_num, i, j)
            car_seats.append(seat)
            seat_num += 1

    return car, car_seats


def generate_seat(car_id: str, seat_num: int, x_pos: int, y_pos: int):
    seat = SeatModel(
        id=str(uuid.uuid4()),
        car_id=car_id,
        number=seat_num,
        x_pos=x_pos,
        y_pos=y_pos,
    )
    return seat

def generate_compositions():
    train_compositions_num = paths_creator.NUMBER_OF_PATHS
    for _ in range(train_compositions_num):
        composition = generate_composition()
        compositions.append(composition.__dict__)

    save_json_file("trains", trains)
    save_json_file("cars", cars)
    save_json_file("seats", seats)
    save_json_file("compositions", compositions)
    save_json_file("compositions_cars", compositions_cars)

# if __name__ == "__main__":
#     generate_compositions()
