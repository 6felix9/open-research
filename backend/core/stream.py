import json


def sse(event: str, data) -> dict:
    return {"event": event, "data": json.dumps(data)}
