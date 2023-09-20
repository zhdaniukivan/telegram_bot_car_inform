import os
from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str            # Токен для доступа к телеграм-боту


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN')))

# HOST = os.getenv('HOST')
# PASSWORD = os.getenv('PASSWORD')
# USER = os.getenv('USER')
# NAME = os.getenv('NAME')
# PORT = 5432

HOST = 'localhost'
USER = 'postgres5'
PASSWORD = 'qwerty5'
NAME = 'car_bot'
PORT = 5432





POSTGRES_URL = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}'
print(POSTGRES_URL)