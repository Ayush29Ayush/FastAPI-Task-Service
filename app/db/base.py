from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

class Base(DeclarativeBase):
    # You can define common attributes or metadata here
    metadata = MetaData()