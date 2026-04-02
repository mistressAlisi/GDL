import json, uuid

class JSONProtocol:
    @staticmethod
    def make_request(action, filters=None, settings=None, request_id=None):
        return {
            "action": action,
            "request_id": request_id or str(uuid.uuid4()),
            "filters": filters or {},
            "settings": settings or {},
        }

    @staticmethod
    def make_response(event_type, request_id, payload=None):
        d = {"type": event_type, "request_id": request_id}
        if payload:
            d.update(payload)
        return json.dumps(d)
