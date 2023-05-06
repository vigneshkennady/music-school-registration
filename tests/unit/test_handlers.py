# pylint: disable=no-self-use
from __future__ import annotations
from collections import defaultdict
from typing import Dict, List
import pytest
from musicschoolRegistration import bootstrap
from musicschoolRegistration.domain import commands
from musicschoolRegistration.services import handlers
from musicschoolRegistration.adapters import notifications, repository
from musicschoolRegistration.services import unit_of_work

class FakeRepository(repository.AbstractmusicLessonRepository):
    def __init__(self, lessons):
        super().__init__()
        self._lessons = set(lessons)

    def _add(self, lessons):
        self._lessons.add(lessons)

    def _get(self, lesson_name):
        return next((p for p in self._lessons if p.lesson_name == lesson_name), None)

    def _get_by_batchref(self, batchref):
        return next(
            (p for p in self._lessons for b in p.lesson if b.reference == batchref),
            None,
        )
    def _getMusicLesson(self, lesson_name):
        return next((p for p in self._lessons if p.lesson_name == lesson_name), None)

    
    def _update(self, lesson_name,quantity):
        return next((p for p in self._lessons if p.lesson_name == lesson_name), None)


    
class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.lessons = FakeRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass

class FakeNotifications(notifications.AbstractNotifications):
    def __init__(self):
        self.sent = defaultdict(list)  # type: Dict[str, List[str]]

    def send(self, destination, message):
        self.sent[destination].append(message)

def bootstrap_test_app():
    return bootstrap.bootstrap(
        start_orm=False,
        uow=FakeUnitOfWork(),
        notifications=FakeNotifications(),
        publish=lambda *args: None,
    )

class TestAddMusicLesson:
    def test_for_new_musicLesson(self):
        bus = bootstrap_test_app()
        bus.handle(commands.CreateLesson("Violin Beginner",100,"XYZ",5))
        assert bus.uow.lessons.get("Violin Beginner") is not None
        assert bus.uow.committed

    def test_for_existing_musicLesson(self):
        bus = bootstrap_test_app()
        bus.handle(commands.CreateLesson("Violin Beginner",50,"XYZ",5))
        bus.handle(commands.CreateLesson("Violin Beginner",50,"XYZ",5))
        assert "Violin Beginner" in [
            b.lesson_name for b in bus.uow.lessons.get("Violin Beginner").musicLesson
        ]

class TestAllocate:
    def test_allocates(self):
        bus = bootstrap_test_app()
        bus.handle(commands.CreateLesson("Violin Beginner",50,"XYZ",5))
        bus.handle(commands.AllocateService(2345,"Violin Beginner","David"))
        [musicLesson] = bus.uow.lessons.get("Violin Beginner").musicLesson
        assert musicLesson.available_quantity == 4

    def test_errors_for_invalid_service(self):
        bus = bootstrap_test_app()
        bus.handle(commands.CreateLesson("Violin Beginner",50,"XYZ",5))

        with pytest.raises(handlers.InvalidService, match="Invalid service"):
            bus.handle(commands.AllocateService(2345, "NONEXISTENTSERVICE", "David"))

    def test_commits(self):
        bus = bootstrap_test_app()
        bus.handle(commands.CreateLesson("Violin Beginner",50,"XYZ",5))
        bus.handle(commands.AllocateService(2345,"Violin Beginner","David"))
        assert bus.uow.committed