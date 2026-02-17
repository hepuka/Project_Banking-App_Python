from repositories.user_repository import UserRepository

class AuthService:

    @staticmethod
    def authenticate(username, password):
        user = UserRepository.find_by_username(username)

        if user and user["password"] == password: return user
        return None
