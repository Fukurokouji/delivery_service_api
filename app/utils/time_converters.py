from datetime import datetime

from app.utils.constants import TIME_FORMAT


def str_to_time_obj(time: str) -> datetime.time:
    """из строки возвращает объект time по формату, установленном в домене"""
    return datetime.strptime(time, TIME_FORMAT)


def time_obj_to_str(time: datetime.time) -> str:
    """из объекта time возвращает строку по формату, установленном в домене"""
    return time.strftime(TIME_FORMAT)
