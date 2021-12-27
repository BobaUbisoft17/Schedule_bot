"""Модуль с хранилищем расписаний."""

from enum import IntEnum
from pathlib import Path
from typing import List


class ScheduleStatus(IntEnum):
    """Статус расписания.

    - `SAME` - файл расписания есть в хранилище.
    - `NEW` - файла расписания нет в хранилище.
    - `UPDATE` - файл расписания является изменением существующего.
    """

    SAME = 0
    NEW = 1
    UPDATE = 2


class ScheduleRepository:
    """Хранилище расписаний.

    Обёртка над папкой со скачанными расписаниями.
    """

    PATH = Path("schedules")

    def get_all(self) -> List[Path]:
        """Получение всех файлов расписаний."""
        return list(self.PATH.iterdir())

    def save(self, filename: str, content: bytes):
        """Сохранение файла расписания с его содержимым."""
        self.PATH.joinpath(filename).write_bytes(content)

    def check_status(self, schedule_filename: str) -> ScheduleStatus:
        """Получение статуса файла распиания.

        Смотри `ScheduleStatus`.
        """
        schedules_files = self.get_all()
        if schedule_filename not in schedules_files:
            return ScheduleStatus.NEW

        for schedule_file in schedules_files:
            filename = schedule_file.name
            if schedule_file.samefile(schedule_filename):
                return ScheduleStatus.SAME

            schedule_file.unlink()  # ! side effect

            # TODO: объяснение, что значит filename in filename
            if filename in schedule_filename:
                return ScheduleStatus.UPDATE
            else:
                return ScheduleStatus.NEW
