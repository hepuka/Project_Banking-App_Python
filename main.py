import sys
import tty
import termios

from core.bank_app import BankApp
from datetime import datetime
from ui.main_menu import MainMenu


def get_password():
    print("Jelszó: ", end="", flush=True)

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    password = ""

    try:
        tty.setraw(fd)

        while True:
            char = sys.stdin.read(1)

            # Enter
            if char in ("\r", "\n"):
                print()
                break

            # Backspace
            elif char == "\x7f":
                if password:
                    password = password[:-1]
                    print("\b \b", end="", flush=True)

            # Ctrl+C
            elif char == "\x03":
                raise KeyboardInterrupt

            else:
                password += char
                print("*", end="", flush=True)

        return password

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


bank = BankApp()
menu = MainMenu(bank)


while not bank.current_user:

    username = input("Felhasználónév: ")
    password = get_password()

    if bank.login(username, password):

        print(f"""
SIKERES BEJELENTKEZÉS.
Név: {bank.current_user['name']}
Szerepkör: {bank.current_user['role']}
Bejelentkezési idő: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
""")

        menu.show()

    else:
        print("Hibás felhasználónév vagy jelszó!")