LIST_SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "token": {
            "type": "string"
        },
        "start": {
            "type": "string"
        },
        "end": {
            "type": "string"
        }
    },
    "required": [
        "token"
    ]
}

ADD_SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "token": {
            "type": "string"
        },
        "day": {
            "type": "string"
        },
        "time": {
            "type": "string"
        },
        "title": {
            "type": "string"
        },
        "homework_text": {
            "type": "string"
        },
        "homework_img": {
            "type": "string"
        }
    },
    "required": [
        "token",
        "day",
        "time",
        "title"
    ]
}
