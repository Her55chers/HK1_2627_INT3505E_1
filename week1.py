#*import os
import json
from flask import Flask, jsonify, request
from uuid import uuid4

app = Flask(__name__)
DB_FILE = "students_data.txt"

def read():
    if not os.path.exists(DB_FILE):
        return []

    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def write(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route("/")
def index():
    return jsonify({"message": "Hello, API"}), 200
##curl -i http://127.0.0.1:5000/echo  

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200
#curl -i http://127.0.0.1:5000/health  

@app.route("/students/<string:student_id>", methods=["GET"])
def get_student(student_id):
    STUDENTS = read()
    student = next((student for student in STUDENTS if student["id"] == student_id), None)
    if student is None:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(student), 200
#curl -i http://127.0.0.1:5000/students/24010101

@app.route("/students/<string:student_id>", methods=["PUT"])
def update_student(student_id):
    STUDENTS = read()
    student = next((student for student in STUDENTS if student["id"] == student_id), None)
    if student is None:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json(silent=True)

    name = data.get("name")
    age = data.get("age")
    gpa = data.get("gpa")

    if name is not None or name.strip() == "":
        student["name"] = name
        return jsonify({"error": "Name cannot be empty"}), 400
    if age is not None:
        try:
            age = int(age)
            if age < 0:
                return jsonify({"error": "Age must be a positive integer"}), 400
            student["age"] = age
        except (ValueError, TypeError):
            return jsonify({"error": "Age must be a positive integer"}), 400
    if gpa is not None:
        try:
            gpa = float(gpa)
            if gpa < 0 or gpa > 4.0:
                return jsonify({"error": "GPA must be a number between 0 and 4.0"}), 400
            student["gpa"] = gpa
        except (ValueError, TypeError):
            return jsonify({"error": "GPA must be a number between 0 and 4.0"}), 400

    write(STUDENTS)
    return jsonify(student), 200

#curl -i -X PUT http://127.0.0.1:5000/students/24010101
# -H "Content-Type: application/json" 
# -d "{\"name\": \"Nguyen Van B\", \"age\": 21, \"gpa\": 3.67}"

@app.route("/students", methods=["POST"])
def create_student():
    STUDENTS = read()
    data = request.get_json(silent=True)

    id = data.get("id")
    name = data.get("name")
    age = data.get("age")
    gpa = data.get("gpa")   

    if id is None or id.strip() == "":
        return jsonify({"error": "ID is required"}), 400

    if name is None or name.strip() == "": 
        return jsonify({"error": "Name is required"}), 400
    
    if age is None:
        return jsonify({"error": "Age is required"}), 400
    try:
        age = int(age)
    except (ValueError, TypeError):
        return jsonify({"error": "Age must be an positive integer"}), 400
    if age < 0:
        return jsonify({"error": "Age must be a positive integer"}), 400
        
    if gpa is None:
        return jsonify({"error": "GPA is required"}), 400
    try:
        gpa = float(gpa)
    except (ValueError, TypeError):
        return jsonify({"error": "GPA must be a number"}), 400
    if gpa < 0 or gpa > 4.0:
        return jsonify({"error": "GPA must be a number between 0 and 4.0"}), 400
    
    if any(student["id"] == id for student in STUDENTS):
        return jsonify({"error": "Student already exists"}), 400

    student =  {"id": id,
                "name": name,
                "age": age,
                "gpa": gpa}

    STUDENTS.append(student)
    write(STUDENTS)
    return jsonify(student), 201
#curl -i -X POST http://127.0.0.1:5000/students 
# -H "Content-Type: application/json" 
# -d "{\"id\": \"24010101\", \"name\": \"Nguyen Van A\", \"age\": 20, \"gpa\": 3.6}"

@app.route("/echo", methods=["POST"])
def echo():
    data = request.get_json(silent=True)
    if data is None:
        return {"error": "Invalid JSON"}, 400
    return {"you_sent": data}, 200
#curl -i -X POST http://127.0.0.1:5000/echo -H "Content-Type: application/json" -d "{\"name\":\"Tri\"}"  

@app.route("/students/<string:student_id>", methods=["DELETE"])
def delete_student(student_id):
    STUDENTS = read()
    student = next((student for student in STUDENTS if student["id"] == student_id), None)
    if student is None:
        return jsonify({"error": "Student not found"}), 404
    STUDENTS = [s for s in STUDENTS if s["id"] != student_id]
    write(STUDENTS) 
    return jsonify({"message": "Student deleted"}), 200
#curl -i -X DELETE http://127.0.0.1:5000/students/24010101

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True) #both wifi and localhost works fine.
    