from datetime import datetime

class Customer:

    def __init__(self, data: dict):
        self.id = data["id"]
        self.name = data["name"]
        self.email = data["email"]
        self.mothers_maiden_name = data["mothers_maiden_name"]
        self.personal_id_card_number = data["personal_id_card_number"]
        self.address = data["address"]
        self.createdAt = data.get(
            "createdAt",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        self.modifiedAt = data.get("modifiedAt")


    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "mothers_maiden_name": self.mothers_maiden_name,
            "personal_id_card_number": self.personal_id_card_number,
            "address": self.address,
            "createdAt": self.createdAt,
            "modifiedAt": self.modifiedAt
        }










