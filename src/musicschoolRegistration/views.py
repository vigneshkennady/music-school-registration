from musicschoolRegistration.services import unit_of_work
from sqlalchemy.sql import text


def allocations(customerid: int, uow: unit_of_work.SqlAlchemyUnitOfWork):
    with uow:
        query = text("SELECT id,student_id,lesson_name, student_name FROM student_table WHERE student_id = :student_id")
        results = uow.session.execute(query,dict(student_id=customerid))
    
        return  [dict(r._mapping) for r in results]
    