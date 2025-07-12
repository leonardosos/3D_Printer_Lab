# mock_webui_api.py
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/temperature/global', methods=['GET'])
def get_global_temperature():
    return jsonify({
        "temperatures": [
            { "temperature": 23.1, "source": "room", "sourceId": "room-sensor-1", "timestamp": "2025-07-12T10:00:00Z" },
            { "temperature": 205.5, "source": "printer", "sourceId": "printer-1", "timestamp": "2025-07-12T10:00:05Z" },
            { "temperature": 198.2, "source": "printer", "sourceId": "printer-2", "timestamp": "2025-07-12T10:00:07Z" }
        ],
        "lastUpdated": "2025-07-12T10:00:07Z"
    })

@app.route('/printers/status', methods=['GET'])
def get_printers_status():
    return jsonify({
        "printers": [
            {
                "printerId": "printer-1",
                "status": "printing",
                "currentJobId": "job-001",
                "progress": 67,
                "temperature": 205.5,
                "lastUpdated": "2025-07-12T10:00:05Z"
            },
            {
                "printerId": "printer-2",
                "status": "idle",
                "currentJobId": None,
                "progress": None,
                "temperature": 198.2,
                "lastUpdated": "2025-07-12T10:00:07Z"
            }
        ]
    })

@app.route('/jobs', methods=['GET'])
def get_jobs():
    return jsonify({
        "jobs": [
            {
                "id": "job-001",
                "modelId": "model-abc",
                "assignedPrinterId": "printer-1",
                "priority": 10,
                "status": "in_progress",
                "submittedAt": "2025-07-12T09:45:00Z",
                "updatedAt": "2025-07-12T10:00:00Z"
            },
            {
                "id": "job-002",
                "modelId": "model-def",
                "assignedPrinterId": None,
                "priority": 5,
                "status": "queued",
                "submittedAt": "2025-07-12T09:50:00Z",
                "updatedAt": "2025-07-12T09:50:00Z"
            }
        ]
    })

@app.route('/jobs', methods=['POST'])
def post_job():
    req = request.get_json(force=True)
    return jsonify({
        "job": {
            "id": "job-003",
            "modelId": req.get("modelId", "model-xyz"),
            "assignedPrinterId": None,
            "priority": req.get("priority", 7),
            "status": "pending",
            "submittedAt": "2025-07-12T10:01:00Z",
            "updatedAt": "2025-07-12T10:01:00Z"
        }
    }), 201

@app.route('/jobs/<job_id>', methods=['PUT'])
def put_job(job_id):
    req = request.get_json(force=True)
    return jsonify({
        "job": {
            "id": job_id,
            "modelId": "model-abc",
            "assignedPrinterId": "printer-1",
            "priority": req.get("priority", 15),
            "status": "in_progress",
            "submittedAt": "2025-07-12T09:45:00Z",
            "updatedAt": "2025-07-12T10:02:00Z"
        }
    })

@app.route('/jobs/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    return '', 204

@app.before_request
def log_request_info():
    try:
        payload = request.get_data(as_text=True)
        if payload:
            parsed = json.loads(payload)
            print("\n\nIncoming Request\nPayload:", json.dumps(parsed, indent=2))
        else:
            print("\n\nIncoming Request\nPayload: <empty>")
    finally:
        pass

if __name__ == '__main__':
    app.run(port=8080, debug=True)