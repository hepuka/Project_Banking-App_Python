
class User:
    def __init__(self, data: dict):
        self.name = data["name"]
        self.email = data["email"]
        self.username = data["username"]
        self.password = data["password"]
        self.role = data["role"]
