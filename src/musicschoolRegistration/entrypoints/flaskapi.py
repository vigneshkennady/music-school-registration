from flask import Flask, jsonify, request
from musicschoolRegistration import bootstrap, views
from musicschoolRegistration.domain import commands
from musicschoolRegistration.services.handlers import InvalidService

app = Flask(__name__)
bus = bootstrap.bootstrap()


@app.route("/add_lesson", methods=["POST"])
def add_service():

    data = request.get_json()
    print(data)
    #lesson_id = data["lesson_id"]
    lesson_name = data["lesson_name"]
    price = data["price"]
    teacher_name = data["teacher_name"]
    qty = data["qty"]
    print(lesson_name,price,teacher_name)
    
    cmd = commands.CreateLesson(
        lesson_name=lesson_name, price=price, teacher_name=teacher_name, qty=qty
    )
    bus.handle(cmd)
    return "OK", 201

@app.route("/allocate_lesson", methods=["POST"])
def allocate_lesson():
    try:
        cmd = commands.AllocateService(
            request.json["student_id"], request.json["lesson_name"], request.json["student_name"]
        )
        bus.handle(cmd)
    except InvalidService as e:
        return {"message": str(e)}, 400

    return "OK", 202

@app.route("/allocations/<student_id>", methods=["GET"])
def allocations_view_endpoint(student_id):
    print(student_id)
    result = views.allocations(int(student_id), bus.uow)
    if not result:
        return "not found", 404
    return jsonify(result), 200

