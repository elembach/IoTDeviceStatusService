from marshmallow import Schema, fields, validate

# Functions to validate input data format
class StatusSchema(Schema):
    device_id = fields.Str(required=True)
    time_stamp = fields.DateTime(required=True)
    battery_level = fields.Int(required=True, validate=validate.Range(min=0, max=100))
    rssi = fields.Int(required=True)
    online = fields.Bool(required=True)
