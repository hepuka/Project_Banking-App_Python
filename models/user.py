from datetime import datetime

class User:
    def __init__(self, data: dict):
        self.name = data["name"]
        self.email = data["email"]
        self.username = data["username"]
        self.password = data["password"]
        self.role = data["role"]
        self.createdAt = data.get("createdAt", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def user_to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "username": self.username,
            "role": self.role,
            "password": self.password,
            "createdAt": self.createdAt
        }