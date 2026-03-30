import uuid

class Message:
    def __init__(self, source, ttl, payload):
        self.id = str(uuid.uuid4())[:8]
        self.source = source
        self.ttl = ttl
        self.payload = payload

    def encode(self):
        return f"{self.id}|{self.source}|{self.ttl}|{self.payload}"

    @staticmethod
    def decode(data):
        msg_id, source, ttl, payload = data.split("|", 3)
        m = Message(source, int(ttl), payload)
        m.id = msg_id
        return m