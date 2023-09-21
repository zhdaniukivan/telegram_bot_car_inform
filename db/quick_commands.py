from asyncpg import UniqueViolationError

from db.schemas.car_number import CarNumberModel


async def add_number(name: str, number: str, rew: str, id_to_message: int):
    try:
        car_number = CarNumberModel(
            name=name,
            number=number,
            rew=rew,
            id_to_message=id_to_message
        )
        await car_number.create()
    except UniqueViolationError:
        print('Пользователь не добавлен')


async def select_car_number(number: str):
    car_data = await CarNumberModel.query.where(CarNumberModel.number == number).gino.first()
    return car_data
