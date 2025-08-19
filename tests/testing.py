import pytest
from app.validation import StatusSchema
from marshmallow import ValidationError
from app import create_app
import os
import tempfile

# Establishes the schema of the data(format, validation)
status_schema = StatusSchema()


# Sets up a reusable setup function as a "test client"
@pytest.fixture
def client():
    # Makes a temp file to test database with a file descriptor and a path
    db_file_descriptor, db_path = tempfile.mkstemp()
    # Testing config is set up
    test_config = {
        'TESTING': True,
        'DATABASE': db_path,
        'API_KEY': 'supertopsecretkey!'
    }
    app = create_app(test_config)

    # Allows for client requests
    with app.test_client() as client:
        yield client

    # Closes file descriptor and path
    os.close(db_file_descriptor)
    os.unlink(db_path)


# Headers for the authorization key
headers = {"Authorization": "supertopsecretkey!"}


# Tests the api key functionality, incorrect api key should throw 401 error
def test_wrong_auth(client):
    data = {
        "device_id": "computer456",
        "time_stamp": "2025-06-30T09:00:00Z",
        "battery_level": 50,
        "rssi": -50,
        "online": True,
    }
    wrong_headers = {"Authorization": "wrong_key"}
    response = client.post("/status", json=data, headers=wrong_headers)
    assert response.status_code == 401


# Overall test checks when data is in valid format
def test_valid_data():
    valid_data = {
        "device_id": "phone123",
        "time_stamp": "2025-06-30T09:00:00Z",
        "battery_level": 100,
        "rssi": -60,
        "online": True,
    }
    # No errors should be raised
    result = status_schema.load(valid_data)
    assert result["device_id"] == valid_data["device_id"]


# Tests to see if error is thrown when a field is missing
def test_missing_fields():
    invalid_data = {
        "device_id": "ipad121415"
        # Missing all other required fields
    }
    with pytest.raises(ValidationError) as exc_info:
        status_schema.load(invalid_data)
    errors = exc_info.value.messages
    assert "time_stamp" in errors
    assert "battery_level" in errors
    assert "rssi" in errors
    assert "online" in errors


# Tests to see if error is thrown when battery_level is out of range
def test_invalid_battery_level():
    invalid_data = {
        "device_id": "computer456",
        "time_stamp": "2025-06-30T09:00:00Z",
        "battery_level": 150,
        "rssi": -50,
        "online": True,
    }
    with pytest.raises(ValidationError) as exc_info:
        status_schema.load(invalid_data)
    errors = exc_info.value.messages
    assert "battery_level" in errors


# Tests to see if error is thrown when time_stamp is not in proper format
def test_invalid_time_stamp_format():
    invalid_data = {
        "device_id": "thermostat789",
        "time_stamp": "not_a_date",
        "battery_level": 50,
        "rssi": -40,
        "online": True,
    }
    with pytest.raises(ValidationError) as exc_info:
        status_schema.load(invalid_data)
    errors = exc_info.value.messages
    assert "time_stamp" in errors


# Tests to see if error is thrown when online is not a boolean
def test_online_not_boolean():
    invalid_data = {
        "device_id": "tv-101112",
        "time_stamp": "2025-06-09T09:00:00Z",
        "battery_level": 0,
        "rssi": -30,
        "online": "8",
    }
    with pytest.raises(ValidationError) as exc_info:
        status_schema.load(invalid_data)
    errors = exc_info.value.messages
    assert "online" in errors


# Tests to see if status can be posted successfully
def test_post_valid_status(client):
    data = {
        "device_id": "computer123",
        "time_stamp": "2025-07-01T14:00:00Z",
        "battery_level": 90,
        "rssi": -55,
        "online": True
    }
    response = client.post('/status', json=data, headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["device_id"] == "computer123"


# Tests if there is no status, that a 404 error is thrown
def test_get_invalid_status(client):
    response = client.get('/status/device-does-not-exist', headers=headers)
    assert response.status_code == 404
    assert "error" in response.get_json()


# Tests to see if status history is returned
def test_status_history(client):
    first_data = {
        "device_id": "computer456",
        "time_stamp": "2025-06-30T09:00:00Z",
        "battery_level": 50,
        "rssi": -50,
        "online": True,
    }

    first_response = client.post("/status", json=first_data, headers=headers)
    assert first_response.status_code == 200

    second_data = {
        "device_id": "computer456",
        "time_stamp": "2025-06-30T10:00:00Z",
        "battery_level": 40,
        "rssi": -40,
        "online": True,
    }

    second_response = client.post("/status", json=second_data, headers=headers)
    assert second_response.status_code == 200

    third_data = {
        "device_id": "computer456",
        "time_stamp": "2025-06-30T11:00:00Z",
        "battery_level": 50,
        "rssi": -50,
        "online": False,
    }

    third_response = client.post("/status", json=third_data, headers=headers)
    assert third_response.status_code == 200

    fourth_data = {
        "device_id": "computer456",
        "time_stamp": "2025-06-30T12:00:00Z",
        "battery_level": 50,
        "rssi": -50,
        "online": False,
    }

    fourth_response = client.post("/status", json=fourth_data, headers=headers)
    assert fourth_response.status_code == 200

    history_response = client.get(f"/status/computer456/history", headers=headers)
    assert history_response.status_code == 200
    history = history_response.get_json()

    assert history[0]["time_stamp"] == first_data["time_stamp"]
    assert history[1]["time_stamp"] == second_data["time_stamp"]
    assert history[2]["time_stamp"] == third_data["time_stamp"]
    assert history[3]["time_stamp"] == fourth_data["time_stamp"]


# Tests that history for device with no records returns 404 status code
def test_empty_history(client):
    response = client.get("/status/nonexistent-device/history", headers=headers)
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
