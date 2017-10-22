from redis import Redis

class Persistence():
    def __init__(self):
        self.db = Redis(host='redis', port=6379)

    def save_message(self, _id, message):
        self.db.set('messages-' + _id, message)

    def delete_messages(self, _id):
        self.db.delete('messages-' + _id)

    def key_exists(self, _id):
        return self.db.exists('messages-' + _id)

    def load_messages(self, _id):
        return self.db.get('messages-' + _id)

    def submit_payload(self, _id):
        pass