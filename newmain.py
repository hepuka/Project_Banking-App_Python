import json
import uuid
from datetime import datetime
import http.server
import socketserver
import webbrowser
import threading
import urllib.parse
import time
import sys
import random
from typing import Optional, List, Dict

DATABASE_FILE = "database.json"
PORT = 8080

# -------------------- Transaction CLASS --------------------
class Transaction:
    def __init__(self, type_: str, amount: float, timestamp: Optional[str] = None):
        self.type = type_
        self.amount = amount
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def from_dict(cls, data: dict):
        return cls(type_=data["type"], amount=data["amount"], timestamp=data.get("timestamp"))

    def to_dict(self):
        return {"type": self.type, "amount": self.amount, "timestamp": self.timestamp}

# -------------------- CUSTOMER CLASS --------------------
class Customer:
    def __init__(self, data: dict):
        self.id = data["id"]
        self.name = data["name"]
        self.email = data["email"]
        self.account_number = data.get("account_number", self.generate_account_number())
        self.balance = float(data.get("balance", 0.0))
        self.loan_amount = float(data.get("loan_amount", 0.0))
        self.personal_loan_amount = float(data.get("personal_loan_amount", 0.0))
        self.transactions: List[Transaction] = [
            Transaction.from_dict(t) for t in data.get("transactions", [])
        ]
        self.createdAt = data.get("createdAt", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "account_number": self.account_number,
            "balance": self.balance,
            "loan_amount": self.loan_amount,
            "personal_loan_amount": self.personal_loan_amount,
            "transactions": [t.to_dict() for t in self.transactions],
            "createdAt": self.createdAt
        }

    # -------------------- TRANSACTIONS --------------------
    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Hibás összeg!")
        self.balance += amount
        self.transactions.append(Transaction("Befizetés", amount))

    def withdraw(self, amount: float):
        if amount <= 0:
            raise ValueError("Hibás összeg!")
        if self.balance - amount < -self.loan_amount:
            raise ValueError("Nincs elegendő fedezet a számlán!")
        self.balance -= amount
        self.transactions.append(Transaction("Kifizetés", amount))

    # -------------------- LOAN --------------------
    def request_account_loan(self):
        if self.loan_amount != 0:
            return False
        self.loan_amount = self.balance * 1.5
        self.transactions.append(Transaction("Számlahitel igénylés", self.loan_amount))
        return True

    def request_personal_loan(self, amount: float):
        if self.personal_loan_amount != 0:
            return False
        if amount <= 0:
            raise ValueError("Hibás összeg!")
        self.personal_loan_amount += amount
        self.balance += amount
        self.transactions.append(Transaction("Személyi hitel igénylés", amount))
        return True

    def repay_personal_loan(self, amount: float):
        if amount <= 0:
            raise ValueError("Hibás összeg!")
        if amount > self.personal_loan_amount:
            amount = self.personal_loan_amount
        self.personal_loan_amount -= amount
        self.balance -= amount
        self.transactions.append(Transaction("Személyi hiteltörlesztés", amount))

    # -------------------- ACCOUNT NUMBER --------------------
    @staticmethod
    def generate_account_number():
        first_block = "1177" + str(random.randint(1000, 9999))
        second_block = str(random.randint(10_000_000, 99_999_999))
        third_block = str(random.randint(10_000_000, 99_999_999))
        return f"{first_block}-{second_block}-{third_block}"

# -------------------- BANK APP CLASS --------------------
class BankApp:
    def __init__(self):
        self.customers: List[Customer] = []
        self.users: List[Dict] = []
        self.current_customer: Optional[Customer] = None
        self.current_user: Optional[dict] = None
        self.httpd: Optional[socketserver.TCPServer] = None
        self.load_data()

    # ---------- DATABASE ----------
    def load_data(self):
        try:
            with open(DATABASE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.customers = [Customer(c) for c in data.get("customers", [])]
                self.users = data.get("users", [])
        except FileNotFoundError:
            print(f"Hiba: {DATABASE_FILE} nem található!")
            sys.exit(1)

    def save_data(self):
        with open(DATABASE_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "customers": [c.to_dict() for c in self.customers],
                "users": self.users
            }, f, indent=2, ensure_ascii=False)

    # ---------- CUSTOMER MANAGEMENT ----------
    def add_customer(self):
        print("Új ügyfél regisztrálása")
        name = input("Név: ")
        email = input("Email: ")
        new_customer = Customer({
            "id": uuid.uuid4().hex[:4],
            "name": name,
            "email": email,
            "balance": 0.0,
            "loan_amount": 0.0,
            "personal_loan_amount": 0.0
        })
        self.customers.append(new_customer)
        self.save_data()
        print(f"Új ügyfél sikeresen létrehozva! Azonosító: {new_customer.id}")

    def find_customer(self):
        customer_id = input("Add meg az ügyfél azonosítóját: ")
        for c in self.customers:
            if c.id == customer_id:
                self.current_customer = c
                print(f"Ügyfél: {c.name}\n")
                return True
        print("Nem található ügyfél ezzel az azonosítóval!")
        return False

    # ---------- CUSTOMER MENU ----------
    def customer_menu(self):
        if not self.find_customer():
            return
        menu = {
            "1": ("Ügyféladatok", self.customer_details),
            "2": ("Befizetés", self.deposit),
            "3": ("Kifizetés", self.withdraw),
            "4": ("Számlahitel igénylés", self.account_loan_menu),
            "5": ("Személyi kölcsön igénylés", self.personal_loan_menu),
            "6": ("Vissza a főmenübe", lambda: None),
            "7": ("Kilépés", self.exit_app)
        }
        self.run_menu(menu)

    def customer_details(self):
        c = self.current_customer
        print(f"Név: {c.name}")
        print(f"E-mail: {c.email}")
        print(f"Számlaszám: {c.account_number}")
        print(f"Egyenleg: {c.balance:.3f} Ft")
        print(f"Hitelkeret: {c.loan_amount:.3f} Ft")
        print(f"Személyi kölcsön: {c.personal_loan_amount:.3f} Ft")
        print("Utolsó 5 tranzakció:")
        for t in c.transactions[-5:]:
            print(f"  {t.timestamp} - {t.type} - {t.amount:.2f} Ft")

    def deposit(self):
        try:
            amount = float(input("Befizetendő összeg: "))
            self.current_customer.deposit(amount)
            self.save_data()
            print("Sikeres tranzakció!")
        except ValueError as e:
            print(e)

    def withdraw(self):
        try:
            amount = float(input("Kifizetendő összeg: "))
            self.current_customer.withdraw(amount)
            self.save_data()
            print("Sikeres tranzakció!")
        except ValueError as e:
            print(e)

    # ---------- LOANS ----------
    def account_loan_menu(self):
        if self.current_customer.request_account_loan():
            self.save_data()
            print(f"Sikeres számlahitel! Keret: {self.current_customer.loan_amount:.3f} Ft")
        else:
            print("Az ügyfél már rendelkezik számlahitelkerettel!")

    def personal_loan_menu(self):
        while True:
            print("\nSzemélyi kölcsön menü")
            print("(1) Kölcsön igénylés")
            print("(2) Törlesztés")
            print("(3) Vissza")
            choice = input("Válassz: ")
            try:
                if choice == "1":
                    amount = float(input("Kölcsön összege: "))
                    self.current_customer.request_personal_loan(amount)
                    self.save_data()
                    print("Személyi kölcsön igénylés sikeres!")
                elif choice == "2":
                    amount = float(input("Törlesztendő összeg: "))
                    self.current_customer.repay_personal_loan(amount)
                    self.save_data()
                    print("Törlesztés sikeres!")
                elif choice == "3":
                    break
                else:
                    print("Ismeretlen választás!")
            except ValueError as e:
                print(e)

    # ---------- GENERIC MENU ----------
    def run_menu(self, menu: dict):
        while True:
            for key, (desc, _) in menu.items():
                print(f"({key}) {desc}")
            choice = input("Válassz: ")
            action = menu.get(choice)
            if action:
                action[1]()
                if choice in ["6", "7"]:
                    break
            else:
                print("Ismeretlen választás!")

    def main_menu(self):
        menu = {
            "1": ("Ügyfélkereső", self.customer_menu),
            "2": ("Ügyfélregisztráció", self.add_customer),
            "3": ("Kilépés", self.exit_app)
        }
        self.run_menu(menu)

    # ---------- EXIT ----------
    def exit_app(self):
        print("Kilépés...")
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
        sys.exit(0)

# -------------------- LOGIN SERVER --------------------
class LoginHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=UTF-8")
        self.end_headers()
        self.wfile.write(bank.HTML.format(error="").encode("utf-8"))

    def do_POST(self):
        length = int(self.headers.get('Content-Length'))
        body = self.rfile.read(length).decode()
        post_data = urllib.parse.parse_qs(body)
        username = post_data.get("username", [""])[0]
        password = post_data.get("password", [""])[0]

        for user in bank.users:
            if user["username"] == username and user["password"] == password:
                bank.current_user = user
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=UTF-8")
                self.end_headers()
                self.wfile.write(
                    "<h3>Sikeres bejelentkezés. Bezárhatod az ablakot.</h3>"
                    "<script>setTimeout(() => window.close(), 1000);</script>".encode("utf-8")
                )
                threading.Thread(target=bank.httpd.shutdown).start()
                return

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=UTF-8")
        self.end_headers()
        self.wfile.write(bank.HTML.format(error="<p style='color:red'>Hibás adatok</p>").encode("utf-8"))

# -------------------- RUN --------------------
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

def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    bank.httpd = socketserver.TCPServer(("", PORT), LoginHandler)
    bank.httpd.serve_forever()

threading.Thread(target=run_server, daemon=True).start()
webbrowser.open(f"http://localhost:{PORT}")

print("Kérlek, jelentkezz be a böngészőben...")
while not bank.current_user:
    time.sleep(0.1)

print(f"\nSIKERES BEJELENTKEZÉS!\nÜgyintéző: {bank.current_user['id']}\n")
bank.main_menu()
