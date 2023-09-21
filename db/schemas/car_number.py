from sqlalchemy import Column, String, VARCHAR, BigInteger, sql

from db.car_bot import BaseModel


class CarNumberModel(BaseModel):
    __tablename__ = 'car_number_model'
    name = Column(String(50), primary_key=True)
    number = Column(VARCHAR(8), primary_key=True)
    rew = Column(String(50), primary_key=True)
    id_to_message = Column(BigInteger, primary_key=True)

    query: sql.select
