from abc import ABC
from dataclasses import dataclass


class Event(ABC):
    pass

@dataclass
class Allocated(Event):
    student_id: int
    lesson_name: str
    student_name: str
    #lesson_id: int

@dataclass
class Deallocated(Event):
    student_id: str
    lesson_name: str
    qty: int


@dataclass
class NotAvailable(Event):
    lesson_name: str
    
