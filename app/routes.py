import functools

from flask import Blueprint, request, jsonify, current_app
from app.validation import StatusSchema
from app.database import get_db

# Creates a Blueprint and validation schema
api_bp = Blueprint("api", __name__)
status_schema = StatusSchema()


# Function that serves to require API key
# Takes in function f as argument
def requires_auth(f):
    @functools.wraps(f)
    # Inner function decorates supplied function given arguments and any keywords
    def decorated(*args, **kwargs):
        # Gets the auth value of the API Key
        auth = request.headers.get("Authorization")
        # Checks is the header provided matches the API Key and returns error if not
        if auth != current_app.config["API_KEY"]:
            return jsonify({"error": "Unauthorized"}), 401
        # If it matches, then original function can be returned
        return f(*args, **kwargs)
    return decorated


# Define route of /status that can accept POST requests(device posts status)
@api_bp.route("/status", methods=["POST"])
@requires_auth
def post_status():
    # Extracts data from JSON file and stores as variable data
    data = request.get_json()
    # Checks for errors within schema and returns them with 400 Error
    errors = status_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    # Opens connection to database for the request and inserts each value from data into device_status table
    # Updates row if device ID is already stored
    db = get_db()
    # Changed from ON CONFLICT clause to INSERT
    db.execute("""
        INSERT INTO device_status (device_id, time_stamp, battery_level, rssi, online)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data["device_id"],
        data["time_stamp"],
        data["battery_level"],
        data["rssi"],
        data["online"]
    ))
    db.commit()
    # Returns data submitted in JSON format and success code 200
    return jsonify(data), 200


# GET endpoint that retrieves status based on determined device_id
@api_bp.route("/status/<device_id>", methods=["GET"])
@requires_auth
def get_status(device_id):
    # Gets the database connection and selects device_status from the given device_id
    db = get_db()
    # Changed to select the most recent device status from a given device id
    cursor = db.execute("""
        SELECT * FROM device_status
        WHERE device_id = ?
        ORDER BY time_stamp DESC
        LIMIT 1
    """, (device_id,))
    # Returns the row
    row = cursor.fetchone()
    # If there is no existing matching row with that device_id, throws 404 error
    if row is None:
        return jsonify({"error": "Device not found"}), 404
    # Returns row of values into dictionary and returns in JSON format
    return jsonify(dict(row))


# GET endpoint that retrieves the summary of all devices and their last updated status
@api_bp.route("/status/summary", methods=["GET"])
@requires_auth
def get_summary():
    # Gets the database connection and selects all rows from device_status table
    db = get_db()
    cursor = db.execute("""
        SELECT device_id, battery_level, online, time_stamp
        FROM device_status
        WHERE (device_id, time_stamp) IN (
            SELECT device_id, MAX(time_stamp)
            FROM device_status
            GROUP BY device_id
        )
    """)
    rows = cursor.fetchall()
    # If rows is empty, prompt error
    if not rows:
        return jsonify({"error": "Summary not found"}), 404
    # Returns all values in JSON format
    return jsonify([dict(r) for r in rows])


# GET endpoint that retrieves the history of a device's statuses
@api_bp.route("/status/<device_id>/history", methods=["GET"])
@requires_auth
def get_status_history(device_id):
    db = get_db()
    # Return all devices ordered by time
    cursor = db.execute("""
            SELECT * FROM device_status
            WHERE device_id = ?
            ORDER BY time_stamp     
        """, (device_id,))
    rows = cursor.fetchall()
    # If rows is empty, prompt error
    if not rows:
        return jsonify({"error": "History not found"}), 404
    # Returns all values in JSON format
    return jsonify([dict(r) for r in rows])
