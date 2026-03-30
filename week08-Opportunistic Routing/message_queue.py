import uuid

class Message:
    def __init__(self, content, source, ttl):
        self.id = str(uuid.uuid4())[:8]
        self.content = content
        self.source = source
        self.ttl = ttl

    def encode(self):
        return f"{self.id}|{self.source}|{self.ttl}|{self.content}"

    @staticmethod
    def decode(data):
        msg_id, source, ttl, content = data.split("|", 3)
        msg = Message(content, source, int(ttl))
        msg.id = msg_id
        return msg


class MessageQueue:
    def __init__(self):
        self.buffer = []

    def add(self, msg):
        if msg.id not in [m.id for m in self.buffer]:
            self.buffer.append(msg)
            return True
        return False

    def get_all(self):
        return self.buffer