import time
import webbrowser
from core.bank_app import BankApp
from web.login_server import LoginServer
from datetime import datetime
from ui.main_menu import MainMenu


PORT = 8080

bank = BankApp()
menu = MainMenu(bank)
login = LoginServer(bank, PORT)

bank.HTML = """
<!doctype html>
<html>
<head>
<meta charset="UTF-8">
<title>Bejelentkezés</title>
</head>
<body>
<h2>Add meg a bejelentkező adatokat!</h2>
<form method="post">
<input name="username" placeholder="Felhasználónév" required><br><br>
<input name="password" type="password" placeholder="Jelszó" required><br><br>
<button type="submit">Belépés</button>
</form>
{error}
</body>
</html>
"""

login.start()
webbrowser.open(f"http://localhost:{PORT}")

print("Kérlek, jelentkezz be a böngészőben...")
while not bank.current_user:
    time.sleep(0.1)

print(f"""
SIKERES BEJELENTKEZÉS.
Név: {bank.current_user['name']}
Szerepkör: {bank.current_user['role']}
Idő: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
""")

menu.show()
