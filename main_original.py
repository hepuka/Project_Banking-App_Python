import json
import uuid
from datetime import datetime
import http.server
import socketserver
import webbrowser
import threading
import urllib.parse
import time
from typing import Optional
import sys
import random

data = []
current_customer = None
current_user =  None
httpd: Optional[socketserver.TCPServer] = None
server_thread = None
server_running = True
main_menu = True
customer_menu = False
loan_menu = False

def load_data():
    try:
        with open("database.json", "r", encoding="utf-8") as file:
            global data
            data = json.load(file)
    except FileNotFoundError:
        print("Error: The file 'database.json' was not found.")
        quit()

def get_customer():
    global current_customer, main_menu, customer_menu
    load_data()
    customer_id = input("Add meg az ügyfél azonosítóját:\n")
    for customer in data["customers"]:
        if customer["id"] == customer_id:
            current_customer = customer
            print("SIKERES ÜGYFÉLAZONOSÍTÁS")
            print(f"Név: {current_customer['name']}")
            main_menu = False
            customer_menu= True
            break

    if current_customer is None:
        print("Nem található ügyfél ezzel az azonosítóval!")
        return

def save_database():
    with open("database.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

def customer_details():
    global current_customer
    print(f"Név: {current_customer['name']}")
    print(f"E-mail: {current_customer['email']}")
    print(f"Számlaszám: {current_customer['account_number']}")
    print(f"Egyenleg: {current_customer['balance']:.3f} Ft")
    print(f"Hitelkeret: {current_customer['loan_amount']:.3f} Ft")

def deposit():
    global current_customer
    amount = int(input("BEFIZETENDŐ ÖSSZEG: "))

    if amount < 0:
        print("HIBÁS ÖSSZEG!")
        return

    current_customer["balance"] += amount
    save_database()
    print("SIKERES TRANZAKCIÓ!")

def withdraw():
    global current_customer
    balance = current_customer["balance"]
    loan = current_customer["loan_amount"]
    amount = int(input("KIFIZETENDŐ ÖSSZEG: "))

    if amount < 0:
        print("HIBÁS ÖSSZEG!")
        return

    if balance - amount < loan:
        print("NINCS ELEGENDŐ FEDEZET A SZÁMLÁN!")
        return

    balance -= amount
    current_customer["balance"] = balance
    save_database()
    print("SIKERES TRANZAKCIÓ!")

def exit_app():
    global httpd
    print("SIKERES KILÉPÉS")

    if httpd:
        httpd.shutdown()
        httpd.server_close()

    sys.exit(0)

def get_account_loan():
    global current_customer
    balance = current_customer["balance"]
    loan = current_customer["loan_amount"]

    if loan == 0.00:
        loan_amount = balance * 1.20
        current_customer["loan_amount"] = -loan_amount
        save_database()
        print("SIKERES HITELIGÉNYLÉS!")
        print(f"HITELKERET: -{loan_amount:.3f} Ft")
    else:
        print("AZ ÜGYFÉL MÁR RENDELKEZIK SZÁMLAHITELLEL!")

def generate_account_number():
    def random_block(eight_digits=True):
        if eight_digits:
            return str(random.randint(10_000_000, 99_999_999))
        else:
            return str(random.randint(1000, 9999))

    first_block = "1177" + str(random.randint(1000, 9999))
    second_block = random_block()
    third_block = random_block()

    return f"{first_block}-{second_block}-{third_block}"

def add_new_customer():
    load_data()
    print("ÚJ ÜGYFÉL REGISZTRÁLÁSA")
    name = input("Név: ")
    email = input("Email: ")

    new_customer = {
        "id": uuid.uuid4().hex[:4],
        "name": name,
        "email": email,
        "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "account_number": generate_account_number(),
        "balance": 0.000,
        "loan_amount": 0.000,
        "personal_loan_amount": 0.000
    }

    data["customers"].append(new_customer)
    save_database()
    print("ÚJ ÜGYFÉL SIKERESEN HOZZÁADVA!")

def back_to_main_menu():
    global main_menu, customer_menu, current_customer
    customer_menu = False
    main_menu = True
    current_customer = None

def enter_loan_menu():
    global loan_menu, customer_menu
    customer_menu = False
    loan_menu = True

def loan_details():
    global current_customer
    print(f"Név: {current_customer['name']}")
    print(f"Hitelkeret: {current_customer['loan_amount']:.3f} Ft")
    print(f"Számlaegyenleg: {current_customer['balance']:.3f} Ft")

def get_personal_loan():
    pass

def personal_loan_deposit():
    pass

def back_to_customer_menu():
    global loan_menu, customer_menu
    loan_menu = False
    customer_menu = True

# ---------------- LOGIN ----------------
login_result = {"user": None}

PORT = 8080

HTML = """
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

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=UTF-8")
        self.end_headers()
        self.wfile.write(HTML.format(error="").encode("utf-8"))

    def do_POST(self):
        length = int(self.headers.get('Content-Length'))
        body = self.rfile.read(length).decode()
        post_data = urllib.parse.parse_qs(body)
        username = post_data.get("username", [""])[0]
        password = post_data.get("password", [""])[0]
        load_data()

        for user in data["users"]:
            if user["username"] == username and user["password"] == password:
                login_result["user"] = user

                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=UTF-8")
                self.end_headers()
                self.wfile.write(
                    "<h3>Sikeres bejelentkezés. Az ablak bezáródik.</h3>"
                    "<script>setTimeout(() => window.close(), 1000);</script>"
                    .encode("utf-8")
                )

                threading.Thread(target=httpd.shutdown).start()
                return

        # Hibás login
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=UTF-8")
        self.end_headers()
        self.wfile.write(HTML.format(error="<p style='color:red'>Hibás adatok</p>").encode("utf-8"))

def run_server():
    global httpd
    socketserver.TCPServer.allow_reuse_address = True

    httpd = socketserver.TCPServer(("", PORT), Handler)
    httpd.serve_forever()

server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()
webbrowser.open(f"http://localhost:{PORT}")

print("Kérlek, jelentkezz be a böngészőben...")
while login_result["user"] is None:
    time.sleep(0.1)

current_user = login_result["user"]
print("SIKERES BEJELENTKEZÉS")
print(f"Ügyintéző: {current_user['id']}")

# ---------------- MENU ----------------
while True:
    if main_menu:
        print("\n-------- FŐMENÜ --------")
        print("(1) ÜGYFÉLKERESŐ")
        print("(2) ÜGYFÉLREGISZTRÁCIÓ")
        print("(3) KILÉPÉS\n")

        choice = input("VÁLASSZ (1-3): ")
        match choice:
            case "1":
                get_customer()
            case "2":
                add_new_customer()
            case "3":
                exit_app()
            case _:
                print("ISMERETLEN MENÜ!")

    elif customer_menu:
        print("\n-------- ÜGYFÉLMENÜ --------")
        print("(1) ÜGYFÉLADATOK")
        print("(2) BEFIZETÉS")
        print("(3) KIFIZETÉS")
        print("(4) HITEL")
        print("(5) VISSZA A FŐMENÜBE")
        print("(6) KILÉPÉS\n")

        choice = input("VÁLASSZ (1-6): ")
        match choice:
            case "1":
                customer_details()
            case "2":
                deposit()
            case "3":
                withdraw()
            case "4":
               enter_loan_menu()
            case "5":
                back_to_main_menu()
            case "6":
                exit_app()
            case _:
                print("ISMERETLEN MENÜ!")

    elif loan_menu:
        print("\n-------- HITELMENÜ --------")
        print("(1) HITELADATOK")
        print("(2) SZÁMLAHITEL IGÉNYLÉS")
        print("(3) SZEMÉLYIHITEL IGÉNYLÉS")
        print("(4) TÖRLESZTŐRÉSZLET BEFIZETÉS")
        print("(5) VISSZA AZ ÜGYFÉLMENÜBE")
        print("(6) VISSZA A FŐMENÜBE")
        print("(7) KILÉPÉS\n")

        choice = input("VÁLASSZ (1-7): ")
        match choice:
            case "1":
                loan_details()
            case "2":
                get_account_loan()
            case "3":
                get_personal_loan()
            case "4":
                personal_loan_deposit()
            case "5":
                back_to_customer_menu()
            case "6":
                back_to_main_menu()
            case "7":
                exit_app()
            case _:
                print("ISMERETLEN MENÜ!")

