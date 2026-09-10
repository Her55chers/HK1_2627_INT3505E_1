from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def index():
    return {"message": "Hello, API"}
if __name__ == "__main__":
    app.run(host="192.168.1.175", port=5000, debug=True) #both wifi and localhost works fine.
