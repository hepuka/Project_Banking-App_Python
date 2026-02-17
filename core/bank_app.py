from services.auth_service import AuthService

class BankApp:
    def __init__(self):
        self.current_user = None
        self.current_customer = None
        self.current_menu = None

    def login(self, username, password):
        user = AuthService.authenticate(username, password)
        if user:
            self.current_user = user
            return True
        return False
