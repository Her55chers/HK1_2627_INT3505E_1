from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({"message": "Hello, API"}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/echo", methods=["POST"])
def echo():
    data = request.get_json(silent=True)
    if data is None:
        return {"error": "Invalid JSON"}, 400
    return {"you_sent": data}, 200

if __name__ == "__main__":
    app.run(host="192.168.1.175", port=5000, debug=True) #both wifi and localhost works fine.