import os
from datetime import datetime
from flask import Flask, jsonify, request
from google.cloud import firestore
from google.cloud import logging as gcloud_logging
##def
PROJECT_ID = os.environ.get("PROJECT_ID")
APP_VERSION = os.environ.get("APP_VERSION", "v1")
COLLECTION = os.environ.get("NOTES_COLLECTION", "notes")

app = Flask(__name__)

# Structured logging to Cloud Logging
glogger_client = gcloud_logging.Client()
glogger_client.setup_logging()

# Firestore client (uses Cloud Run service account)
db = firestore.Client(project=PROJECT_ID)

@app.get("/health")
def health():
    return jsonify({"status": "ok", "version": APP_VERSION}), 200

@app.get("/notes")
def list_notes():
    docs = db.collection(COLLECTION).order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
    items = []
    for d in docs:
        data = d.to_dict()
        items.append({
            "id": d.id,
            "message": data.get("message", ""),
            "timestamp": data.get("timestamp", ""),
            "version": data.get("version", "v1"),
            "title": data.get("title")
        })
    return jsonify(items), 200

@app.post("/notes")
def create_note():
    payload = request.get_json(silent=True) or {}
    message = payload.get("message")
    title = payload.get("title")
    if not message:
        return jsonify({"error": "message is required"}), 400
    doc = {
        "message": message,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": APP_VERSION
    }
    if title:
        doc["title"] = title

    ref = db.collection(COLLECTION).add(doc)[1]
    return jsonify({"id": ref.id, **doc}), 201

@app.delete("/notes/<note_id>")
def delete_note(note_id):
    ref = db.collection(COLLECTION).document(note_id)
    if not ref.get().exists:
        return jsonify({"error": "not found"}), 404
    ref.delete()
    return "", 204

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")), debug=False)
