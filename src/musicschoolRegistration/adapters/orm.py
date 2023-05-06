import logging
#from typing import Text

from sqlalchemy import (
    Table,
    MetaData,
    Column,
    Integer,
    String,
    Date,
    ForeignKey,
    event,
)

# from sqlalchemy.orm import mapper
from sqlalchemy.orm import  registry,mapper, relationship

from musicschoolRegistration.domain import models

mapper_registry = registry()
Base = mapper_registry.generate_base()


logger = logging.getLogger(__name__)

metadata = mapper_registry.metadata

musicLesson = Table(
   "musicLesson",
    metadata,
    Column("lesson_id", Integer, primary_key=True, autoincrement=True),
    Column("lesson_name", ForeignKey("lesson.lesson_name")),
    Column("price", Integer),
    Column("teacher_name", String(255)),
    Column("qty", Integer)
   
)

'''CREATE TABLE "student_table" (
	"id"	INTEGER NOT NULL,
	"student_name"	TEXT NOT NULL,
	"lesson_name"	TEXT NOT NULL,
	"student_id"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
)'''
student_table = Table(
    "student_table",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("student_id", Integer),
    Column("student_name", String(255),nullable=False),
    Column("lesson_name", String(255), nullable=False),
    Column("qty",Integer)
)

'''CREATE TABLE "allocate_lesson" (
	"id"	INTEGER NOT NULL,
	"student_id"	INTEGER NOT NULL,
	"lesson_id"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
	FOREIGN KEY ("student_id") REFERENCES student_table("student_id")
	FOREIGN KEY("lesson_id") REFERENCES musicLesson("lesson_id")
)'''
allocations = Table(
    "allocate_lesson",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("student_id", ForeignKey("student_table.student_id")),
    Column("lesson_id", ForeignKey("musicLesson.lesson_id")),
)

lesson = Table(
    "lesson",
    metadata,
    Column("lesson_name", String(255), primary_key=True),
    Column("version_number", Integer, nullable=False, server_default="0"),
)


# def start_mappers():
#     logger.info("string mappers")
#     # SQLAlchemy 2.0
   
#     batches_mapper = mapper(
#         models.PetService,
#         petService)
#     # SQLAlchemy 1.3
#     # bookmarks_mapper = mapper(Bookmark, bookmarks)

def start_mappers():
    
    print("starting mappers")
    logger.info("Starting mappers")
    student_mapper = mapper_registry.map_imperatively(models.Student, student_table)
    musiclesson_mapper = mapper_registry.map_imperatively(
        models.MusicLesson,
        musicLesson,
        properties={
            "_allocations": relationship(
                student_mapper,
                secondary=allocations,
                collection_class=set,
            )
        },
    )
    mapper_registry.map_imperatively(
        models.Lesson,
        lesson,
        properties={"musicLesson": relationship(musiclesson_mapper)},
    )

@event.listens_for(models.Lesson, "load")
def receive_load(lesson, _):
    lesson.events = []