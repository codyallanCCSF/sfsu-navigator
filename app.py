import json, os
from functools import lru_cache
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

load_dotenv()
app = Flask(__name__, static_folder="static")

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
MAX_QUESTION_LEN = 500

@lru_cache(maxsize=None)
def load(name):
    with open(os.path.join(DATA_DIR, name)) as f:
        return json.load(f)

@app.get("/")
def index():
    return send_from_directory("static", "index.html")

@app.get("/api/places")
def places():
    return jsonify(load("places.json"))

@app.get("/api/events")
def events():
    return jsonify(load("events.json"))

@app.get("/api/buildings")
def buildings():
    return jsonify(load("buildings.json"))

@app.get("/api/graph")
def graph():
    return jsonify(load("building_graph.json"))

@app.post("/api/ask")
def ask():
    body = request.get_json(silent=True)
    question = body.get("question", "") if isinstance(body, dict) else ""
    question = str(question).strip()[:MAX_QUESTION_LEN]
    # TODO (backend owner): call Gemini with places/events, return real results
    return jsonify({"answer": "Stub reply to: " + question, "place_ids": [],
                    "event_ids": [], "route": None})

if __name__ == "__main__":
    app.run(port=8080, debug=os.environ.get("FLASK_DEBUG") == "1")
