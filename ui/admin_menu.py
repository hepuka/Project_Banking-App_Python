from ui.base_menu import BaseMenu
from repositories.user_repository import UserRepository
from datetime import datetime

class AdminMenu(BaseMenu):

    def show(self):
        menu = {
            "1": ("Új felhasználó hozzáadása", self.add_user),
            "2": ("Felhasználók listázása", self.get_users),
            "3": ("Felhasználó adatainak módosítása", self.edit_user),
            "4": ("Felhasználó törlése", self.delete_user),
            "0": ("Kilépés a programból", self.exit_app)
        }

        self.run(menu, "Felhasználókezelés")

    def add_user(self):
        name = input("Név: ")
        email = input("Email: ")
        username = input("Felhasználónév: ")
        password = input("Jelszó: ")
        tmp = input("Szerepkör: (1)user (2)admin:")
        role = "user" if tmp == "1" else "admin"

        user_data = {
            "name": name,
            "email": email,
            "username": username,
            "password": password,
            "role": role,
            "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        UserRepository.create_user(user_data)
        print(f"\nFelhasználó sikeresen létrehozva. Név: {user_data['name']} ")

        self.after_action_menu()

    def get_users(self):
        users = UserRepository.get_all()

        if not users:
            print("\nNincs rögzített felhasználó!")
            return

        print("\nFELHASZNÁLÓK")
        print(
            f"{'Név'.ljust(20)} | "
            f"{'Email'.ljust(20)} | "
            f"{'Szerepkör'.ljust(10)} | "
            f"{'Felhasználónév'.ljust(20)} | "
            f"{'Létrehozva'.ljust(20)} | "
            f"{'Módosítva'.ljust(20)} | "
            f"{'Utolsó bejelentkezés'.ljust(25)}"
        )
        print("-" * 150)

        for u in users:

            login_history = u.get("login_history", [])

            if login_history:
                last_login = login_history[-1].get("loginAt", "-")
            else:
                last_login = "-"

            print(
                f"{u.get('name', '').ljust(20)} | "
                f"{u.get('email', '').ljust(20)} | "
                f"{u.get('role', '').ljust(10)} | "
                f"{u.get('username', '').ljust(20)} | "
                f"{u.get('createdAt', '').ljust(20)} | "
                f"{u.get('modifiedAt', '-').ljust(20)} | "
                f"{last_login.ljust(25)}"
            )

        self.after_action_menu()

    def edit_user(self):
        username = input("Add meg a felhasználónevet: ")
        user = UserRepository.find_by_username(username)

        if not user:
            print("Felhasználó nem található!")
            return

        print("\n--- Felhasználó adatainak módosítása ---")
        print("(Enter = a megadott adat változatlan marad)\n")

        name = input(f"Név [{user.get('name')}]: ").strip()
        email = input(f"Email [{user.get('email')}]: ").strip()
        role_tmp = input(f"Szerepkör: (1)user (2)admin [{user.get('role')}]: ").strip()
        role = "user" if role_tmp == "1" else "admin"

        updates = {}
        if name:
            updates["name"] = name
        if email:
            updates["email"] = email
        if role:
            updates["role"] = role

        updates["username"] = username
        updates["createdAt"] = user.get("createdAt")
        updates["modifiedAt"] = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        UserRepository.update_user(username, updates)
        print("\nA felhasználó adatai sikeresen módosítva!")

        self.after_action_menu()

    def delete_user(self):
        username = input("Add meg a törlendő felhasználó felhasználónevét: ")
        user = UserRepository.find_by_username(username)

        if not user:
            print("\nNincs ilyen regisztrált felhasználó.")
            self.after_action_menu()
            return True

        tmp = input(f"Biztosan törölni szeretnéd a - {username} - felhasználót? (I) Igen (N) Mégsem: ").lower()
        if tmp=="i":
            UserRepository.delete_user(username)
            print("\nFelhasználó sikeresen törölve")
            self.after_action_menu()
            return True
        else:
            print("\nFelhasználó törlése megszakítva.")
            self.after_action_menu()
            return True

