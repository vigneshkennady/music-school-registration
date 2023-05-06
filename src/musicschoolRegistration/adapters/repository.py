import abc
from typing import Set
from musicschoolRegistration.domain import models
from musicschoolRegistration.adapters import orm



class AbstractmusicLessonRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[model.Lesson]

    def add(self, lesson: models.Lesson):
        self._add(lesson)
        self.seen.add(lesson)

    def get(self, lesson_name) -> models.Lesson:
        lesson = self._get(lesson_name)
        if lesson:
            self.seen.add(lesson)
        return lesson
    
    def get_by_lesson_name(self, lesson_name) -> models.Lesson:
        lesson = self.get_by_lesson_name(lesson_name)
        if lesson:
            self.seen.add(lesson)
        return lesson
    
    def updateServiceQty(self, lesson_name,qty) -> models.Lesson:
        lesson = self._getMusicLesson(lesson_name)
        if(lesson.qty >= qty):
            lesson = self._update(lesson_name,lesson.qty - qty)
        
        

    @abc.abstractmethod
    def _add(self, lesson: models.Lesson):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, lesson_name) -> models.Lesson:
        raise NotImplementedError
    
    @abc.abstractmethod
    def _getMusicLesson(self, lesson_name) -> models.MusicLesson:
        raise NotImplementedError
    
    @abc.abstractmethod
    def _update(self, lesson_name,qty) -> models.Lesson:
        raise NotImplementedError

class SqlAlchemymusicLessonRepository(AbstractmusicLessonRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session


    def _add(self, lesson):
        self.session.add(lesson)
        

    def _get(self, lesson_name):
        return self.session.query(models.Lesson).filter_by(lesson_name=lesson_name).first()
    
    def _getMusicLesson(self, lesson_name):
        return self.session.query(models.MusicLesson).filter_by(lesson_name=lesson_name).first()
    
    def _update(self, lesson_name,quantity):
        return self.session.query(models.MusicLesson).filter_by(lesson_name=lesson_name).update({models.MusicLesson.qty:quantity},synchronize_session = False)

    def _get_by_batchref(self, lesson_name):
        return (
            self.session.query(models.Lesson)
            .join(models.MusicLesson)
            .filter(
                orm.musicLesson.lesson_name == lesson_name,
            )
            .first()
        )
    
