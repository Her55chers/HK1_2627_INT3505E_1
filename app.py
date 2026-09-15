from flask import Flask, jsonify, request
from uuid import uuid4

app = Flask(__name__)
STUDENTS = []

@app.route("/")
def index():
    return jsonify({"message": "Hello, API"}), 200
##curl -i http://192.168.1.175:5000/echo  

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200
#curl -i http://192.168.1.175:5000/health  

@app.route("/students", methods=["POST"])
def create_student():
    data = request.get_json(silent=True)

    name = data.get("name")
    age = data.get("age")
    gpa = data.get("gpa")   

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
    
    if any(student["name"] == name for student in STUDENTS): # todo: check by id not name.
        return jsonify({"error": "Student already exists"}), 400

    student = {"id": str(uuid4()),
                "name": name,
                "age": age,
                "gpa": gpa}

    STUDENTS.append(student)
    return jsonify(student), 201

@app.route("/echo", methods=["POST"])
def echo():
    data = request.get_json(silent=True)
    if data is None:
        return {"error": "Invalid JSON"}, 400
    return {"you_sent": data}, 200
#curl -i -X POST http://192.168.1.175:5000/echo -H "Content-Type: application/json" -d "{\"name\":\"Tri\"}"  

if __name__ == "__main__":
    app.run(host="192.168.1.175", port=5000, debug=True) #both wifi and localhost works fine.