#add service
#update service
#delete service
#list all services

from __future__ import annotations
from dataclasses import asdict
from typing import List, Dict, Callable, Type, TYPE_CHECKING
from musicschoolRegistration.domain import commands, events, models
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from musicschoolRegistration.adapters import notifications
    from . import unit_of_work

class InvalidService(Exception):
    pass

def add_lesson(
    cmd: commands.CreateLesson,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        # look to see if we already have this bookmark as the title is set as unique
        lesson = uow.lessons.get(lesson_name=cmd.lesson_name)
        if lesson is None:
            print("Inside if")
            print(cmd.lesson_name,cmd.price,cmd.teacher_name,cmd.qty)

            lesson = models.Lesson(cmd.lesson_name, musicLesson=[])
            uow.lessons.add(lesson)
            lesson.musicLesson.append(models.MusicLesson(cmd.lesson_name, cmd.price,cmd.teacher_name,cmd.qty))
        else:
            print("Already Available")
        uow.commit()

def allocate(
    cmd: commands.AllocateService,
    uow: unit_of_work.AbstractUnitOfWork,
):
    print(cmd.student_id, cmd.lesson_name, cmd.student_name)
    student = models.Student(cmd.student_id, cmd.lesson_name, cmd.student_name,1)
    print(student)
    with uow:
        lesson = uow.lessons.get(lesson_name=student.lesson_name)
        if lesson is None:
            raise InvalidService(f"Invalid service {student.lesson_name}")
        print(lesson.lesson_name)
        lesson.allocate(student)
       
        print("Out of update")
        uow.commit()

def reallocate(
    event: events.Deallocated,
    uow: unit_of_work.AbstractUnitOfWork,
):
    allocate(commands.Allocate(**asdict(event)), uow=uow)


def change_batch_quantity(
    cmd: commands.ChangeBatchQuantity,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        lesson = uow.lessons.get_by_batchref(lesson_name=cmd.lesson_name)
        lesson.change_batch_quantity(lesson_name=cmd.lesson_name, qty=cmd.qty)
        uow.commit()


def publish_allocated_event(
    event: events.Allocated,
    publish: Callable,
):
    publish("lesson_allocated", event)

def send_out_of_stock_notification(
    event: events.NotAvailable,
    notifications: notifications.AbstractNotifications,
):
    notifications.send(
        "stock@made.com",
        f"Service not available for {event.lesson_name}",
    )


EVENT_HANDLERS = {
    
    events.Allocated: [publish_allocated_event],
    events.Deallocated: [reallocate],
    events.NotAvailable: [send_out_of_stock_notification],
    
}  # type: Dict[Type[events.Event], List[Callable]]

COMMAND_HANDLERS = {
    commands.CreateLesson: add_lesson,
    commands.AllocateService: allocate,
    commands.ChangeBatchQuantity: change_batch_quantity,
    
}  
