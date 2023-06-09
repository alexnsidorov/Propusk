from sqlalchemy import (MetaData, Table, Column, Integer,
                        DateTime, String, Text, ForeignKey,
                        create_engine, func)
from sqlalchemy.exc import ProgrammingError
import os
from module.MyMessageBox import show_dialog
from PySide6.QtWidgets import QMessageBox
from logger import logger

meta = MetaData()

# /home/asidorov/Документы/propusk_db

FILE_NAME = None

if os.environ.get("DB_DIR"):
    FILE_NAME = os.path.join(os.environ.get("DB_DIR"), "propusk.db")
else:
    if os.environ.get("DEFAULT_PATH"):
        FILE_NAME = os.path.join(os.environ.get("DEFAULT_PATH"), "propusk.db")
    else:
        logger.error("Не правильно указан путь к базе данных, или вообще отсутствует")
        show_dialog(
            QMessageBox.Icon.Critical,
            "Путь к бд",
            "Не правильно указан путь к базе данных, или вообще отсутствует"
        )
    
cam_setting = Table("сam_setting", meta,
                    Column('id', Integer, primary_key=True),
                    Column('type', Integer, nullable=False),
                    Column('mode', String, nullable=False),
                    Column("selected_cam", String, nullable=False),
                    Column('created', DateTime, default=func.now()),
                    Column('update', DateTime,
                           onupdate=func.current_timestamp())
                    )

list_personal = Table("list_personal", meta,
                      Column('id', Integer, primary_key=True),
                      Column('lastname', String, nullable=False),
                      Column('firstname', String, nullable=False),
                      Column('middlename', String, nullable=False),
                      Column('created', DateTime, default=func.now()),
                      Column('update', DateTime,
                             onupdate=func.current_timestamp())
                      )

list_place = Table("list_place", meta,
                   Column('id', Integer, primary_key=True),
                   Column('name_place', String, nullable=False),
                   Column('created', DateTime, default=func.now()),
                   Column('update', DateTime, onupdate=func.current_timestamp())
                   )

list_propusk = Table("list_propusk", meta,
                     Column("id", Integer, primary_key=True),
                     Column("id_propusk", Integer, nullable=False),
                     Column("date_from", DateTime, nullable=False),
                     Column("date_to", DateTime, nullable=False),
                     Column("personal", Integer, ForeignKey("list_personal.id"), nullable=False),
                     Column("place", Integer, ForeignKey("list_place.id"), nullable=False),
                     Column("receiving_man", Text, nullable=False),
                     Column("purpose_visite", Text, nullable=False),
                     Column("face", Text, nullable=False),
                     Column("document", Text, nullable=False),
                     Column("created", DateTime, default=func.now()),
                     Column("update", DateTime, default=func.now(),
                            onupdate=func.current_timestamp()))

list_ussued_passes = Table("list_ussued_passes", meta,
                           Column("id", Integer, primary_key=True),
                           Column("used_pass", Integer, nullable=False),
                           Column("id_propusk", Integer, ForeignKey("list_propusk.id_propusk"), nullable=False),
                           Column("created", DateTime, default=func.now()),
                           Column("update", DateTime, default=func.now(), onupdate=func.current_timestamp()))

engine = create_engine(F"sqlite:///{FILE_NAME}", echo=False)
engine.logging_name = 'PropuskLogger'

def init_db():
    if not os.path.exists(os.path.dirname(FILE_NAME)):
        os.mkdir(os.path.dirname(FILE_NAME))

    meta.create_all(engine)


def connect():
    return engine.connect()


def check_error_sql(func):
    def wrapper(*arg, **args):
        try:
            return func(arg, args)
        except ProgrammingError as pe:
            logger.error(pe)
            
    return wrapper