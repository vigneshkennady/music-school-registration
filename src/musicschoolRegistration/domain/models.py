from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Set
from . import events, commands

class Lesson:
    def __init__(self, lesson_name: str, musicLesson: List[MusicLesson], version_number: int = 0):
        self.lesson_name = lesson_name
        self.musicLesson = musicLesson
        self.version_number = version_number
        self.events = []  # type: List[events.Event]

    def allocate(self, student: Student) -> str:
        try:
            print("In allocate")
            musiclesson = next(b for b in sorted(self.musicLesson) if b.can_allocate(student))
            musiclesson.allocate(student)
            self.version_number += 1
            self.events.append(
                events.Allocated(
                    student_id=student.student_id,
                    lesson_name=student.lesson_name,
                    student_name=student.student_name,
                    #lesson_id=petservice.lesson_id
                )
            )
            
            return musiclesson.lesson_name
        except StopIteration:
            self.events.append(events.NotAvailable(student.lesson_name))
            return None
        
    def change_batch_quantity(self, lesson_name: str, qty: int):
        musicLesson = next(b for b in self.musicLesson if b.lesson_name == lesson_name)
        musicLesson.qty = qty
        while musicLesson.available_quantity < 0:
            customer = musicLesson.deallocate_one()
            self.events.append(events.Deallocated(student.student_id, student.lesson_name, student.qty))

    


@dataclass(unsafe_hash=True)
class Student:
    student_id: int
    lesson_name: str
    student_name: str  
    qty: 1

class MusicLesson:
    """
	"lesson_id"	INTEGER NOT NULL,
	"lesson_name"	TEXT NOT NULL,
	"price"	INTEGER NOT NULL,
	"teacher_name"	TEXT NOT NULL,
    "qty" INTEGER,
	PRIMARY KEY("lesson_id" AUTOINCREMENT)
    """
    def __init__(self,lesson_name: str,price: int,teacher_name: str,quantity: int):
        #self.lesson_id = lesson_id,
        self.lesson_name = lesson_name
        self.price = price
        self.teacher_name = teacher_name
        self.qty = quantity
        self._allocations = set()
        

    def __repr__(self):
        return f"<MusicLesson {self.lesson_name}>"

    def __eq__(self, other):
        if not isinstance(other, MusicLesson):
            return False
        return other.reference == self.lesson_name

    def __hash__(self):
        return hash(self.lesson_name)

    def allocate(self, student: Student):
        if self.can_allocate(student):
            self._allocations.add(student)
    
    def deallocate_one(self) -> Student:
        return self._allocations.pop()
    

    @property
    def allocated_quantity(self) -> int:
        return sum(customer.qty for customer in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self.qty - self.allocated_quantity

    def can_allocate(self, student: Student) -> bool:
        print(self.available_quantity,student.qty)
        decision = self.lesson_name == student.lesson_name and int(self.available_quantity) >= int(student.qty)
        print(decision)
        return decision

