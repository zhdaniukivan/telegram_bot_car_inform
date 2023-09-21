import asyncio

from data import config_data
from db.car_bot import db
from db import quick_commands as commands


async def db_test():
    await db.set_bind(config_data.POSTGRES_URL)
    await db.gino.drop_all()
    await db.gino.create_all()

    await commands.add_number('stsddfsr', 'stfggr', 'stfdsgfgsfr', 24234132423)
    await commands.add_number('stsdgffdfsr', '1gffggr', 'stfdsqqqqgfgsfr', 124234132423)

    car_number = await commands.select_car_number()


loop = asyncio.get_event_loop()
loop.run_until_complete(db_test())
