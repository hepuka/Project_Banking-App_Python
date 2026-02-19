from models.account import Account
from models.customer import Customer
from repositories.account_repository import AccountRepository
from services.helper_service import Helpers
from ui.base_menu import BaseMenu
from ui.customer_actions_menu import CustomerActionsMenu
from repositories.customer_repository import CustomerRepository
from datetime import datetime
import uuid

class CustomerMenu(BaseMenu):

    def __init__(self, bank):
        super().__init__(bank)

    def show(self):
        menu = {
            "1": ("Új ügyfél regisztráció", self.add_customer),
            "2": ("Ügyfél keresése", self.search_customer),
            "3": ("Ügyfél adatainak módosítása", self.edit_customer),
            "4": ("Új számla igénylés", self.add_new_account),
            "0": ("Kilépés", self.exit_app)
        }

        self.run(menu, "Ügyfélkezelés")

    def search_customer(self):
        customer_id = input("Ügyfél ID: ")
        customer = self.load_customer(customer_id)

        if not customer:
            print("Nem található!")
            return

        CustomerActionsMenu(self.bank).show()

    def add_customer(self):
        account_type_tmp  = input("Számlatípus (1)HUN (2)EUR: ")
        account_type = "HUN" if account_type_tmp == "1" else "EUR"
        name = input("Név: ")
        email = input("Email: ")
        mothers_maiden_name = input("Anyja neve: ")
        personal_id_card_number = input("Személyi igazolvány száma: ")
        post_code = input("Irányítószám: ")
        city = input("Település: ")
        street = input("Utca/Út/Tér: ")
        house_number = input("Házszám/Lépcsőház száma: ")
        floor = input("Emelet: ")
        door_number = input("Ajtó: ")

        customer_data = Customer({
            "id": uuid.uuid4().hex[:8],
            "name": name,
            "email": email,
            "mothers_maiden_name": mothers_maiden_name,
            "personal_id_card_number": personal_id_card_number,
            "address": {
                "post_code": post_code,
                "city": city,
                "street": street,
                "house_number": house_number,
                "floor": floor,
                "door_number": door_number
            }
        })

        CustomerRepository.create_customer(customer_data)

        account_data = {
            "customer_id": customer_data.id,
            "account_type": account_type,
            "account_number": Helpers.generate_account_number(account_type),
            "balance": 0,
            "transactions": []
        }

        if account_type == "HUN":
            account_data["loan_amount"] = 0
            account_data["personal_loan_amount"] = 0

        account = Account(account_data)
        AccountRepository.save(account)

        self.bank.current_customer = customer_data
        print(f"Ügyfél létrehozva! ID: {customer_data.id}")

    def edit_customer(self):
        customer_id = input("Ügyfél ID: ")
        customer = CustomerRepository.find_by_id(customer_id)

        if not customer:
            print("Nincs kiválasztott ügyfél!")
            return

        name = input(f"Új név [{customer.name}]: ").strip()
        email = input(f"Új email [{customer.email}]: ").strip()
        personal_id_card_number = input(f"Új szem.ig.szám [{customer.personal_id_card_number}]: ").strip()
        post_code = input(f"Új irányítószám [{customer.address['post_code']}]: ").strip()
        city = input(f"Új település [{customer.address['city']}]: ").strip()
        street = input(f"Új utca/út/tér [{customer.address['street']}]: ").strip()
        house_number = input(f"Új házszám [{customer.address['house_number']}]: ").strip()
        floor = input(f"Új emelet [{customer.address['floor']}]: ").strip()
        door_number = input(f"Új ajtószám [{customer.address['door_number']}]: ").strip()

        # --- Csak akkor módosítunk, ha valóban írtunk valamit ---
        if name:
            customer.name = name

        if email:
            customer.email = email

        if personal_id_card_number:
            customer.personal_id_card_number = personal_id_card_number

        if post_code:
            customer.address["post_code"] = post_code

        if city:
            customer.address["city"] = city

        if street:
            customer.address["street"] = street

        if house_number:
            customer.address["house_number"] = house_number

        if floor:
            customer.address["floor"] = floor

        if door_number:
            customer.address["door_number"] = door_number

        customer.modifiedAt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        CustomerRepository.save(customer)

        print("Sikeres módosítás!")

    def load_customer(self, customer_id):
        customer = CustomerRepository.find_by_id(customer_id)

        if customer:
            self.bank.current_customer = customer  # itt frissítjük a bank current_customer-t
        return customer

    def add_new_account(self):
        customer_id = input("Add meg az ügyfél azonosítóját: ")
        current_customer = CustomerRepository.find_by_id(customer_id)

        if not current_customer:
            print("Nincs ügyfél ezzel az azonosítóval")
            return

        print(f"Név: {current_customer.name}")
        print(f"Anyja neve: {current_customer.mothers_maiden_name}")

        account_type_tmp = input("Számlatípus (1)HUN (2)EUR: ")
        account_type = "HUN" if account_type_tmp == "1" else "EUR"

        account_data = {
            "customer_id": current_customer.id,
            "account_type": account_type,
            "account_number": Helpers.generate_account_number(account_type),
            "balance": 0,
            "transactions": []
        }

        if account_type == "HUN":
            account_data["loan_amount"] = 0
            account_data["personal_loan_amount"] = 0

        account = Account(account_data)
        AccountRepository.save(account)
        print(f"Új számla sikeresen létrehozva")





