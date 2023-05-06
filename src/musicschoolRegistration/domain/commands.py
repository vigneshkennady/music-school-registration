from dataclasses import dataclass
from typing import Optional

class Command:
    pass


@dataclass
class CreateLesson(Command):
    #lesson_id: int
    lesson_name: str
    price: int
    teacher_name: str
    qty: int


@dataclass
class AllocateService(Command):
    student_id: int
    lesson_name: str
    student_name: str

@dataclass
class ChangeBatchQuantity(Command):
    lesson_name: str
    qty: int
