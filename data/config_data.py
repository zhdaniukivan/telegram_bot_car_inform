import os
from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN')),
                  )


env = Env()
env.read_env()  # Load environment variables from .env

HOST = env.str("HOST")
USER_QL = env.str("USER_QL")
PASSWORD = env.str("PASSWORD")
NAME = env.str("NAME")
PORT = env.int("PORT")

print(HOST)
print(USER_QL)
print(PASSWORD)
print(NAME)
print(PORT)

POSTGRES_URL = f'postgresql://{USER_QL}:{PASSWORD}@{HOST}:{PORT}/{NAME}'
print(POSTGRES_URL)
