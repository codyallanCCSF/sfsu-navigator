import json, os
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

load_dotenv()
app = Flask(__name__, static_folder="static")

def load(name):
    with open(os.path.join("data", name)) as f:
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

@app.get("/api/graph")
def graph():
    return jsonify(load("building_graph.json"))

@app.post("/api/ask")
def ask():
    question = (request.get_json(silent=True) or {}).get("question", "")
    # TODO (backend owner): call Gemini with places/events, return real results
    return jsonify({"answer": "Stub reply to: " + question, "place_ids": [],
                    "event_ids": [], "route": None})

if __name__ == "__main__":
    app.run(port=8080, debug=True)
