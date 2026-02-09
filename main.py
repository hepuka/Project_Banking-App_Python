import time
import webbrowser
from services.bank_app import BankApp
from web.login_server import LoginServer
from datetime import datetime

PORT = 8080
0
bank = BankApp()
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

login = LoginServer(bank, PORT)
login.start()
webbrowser.open(f"http://localhost:{PORT}")

print("Kérlek, jelentkezz be a böngészőben...")
while not bank.current_user:
    time.sleep(0.1)

print(f"\nSIKERES BEJELENTKEZÉS\nÜgyintéző: {bank.current_user['name']}\nSzerepkör: {bank.current_user['role']}\nBejelentkezve: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
bank.main_menu()
bank.main_menu()
