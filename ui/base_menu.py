import sys

class BaseMenu:

    def __init__(self, bank):
        self.bank = bank

    def run(self, menu: dict, title: str):
        while True:
            print("\n----- HEPUKA BANK ZRT. -----")
            print(f"----- {title.upper()} -----\n")

            for key, (desc, _) in menu.items():
                print(f"({key}) {desc}")

            print("------------------------------")

            choice = input("\nVálasztott menüpont: ")
            action = menu.get(choice)

            if action:
                result = action[1]()

                if result is False:
                    break
            else:
                print("\nÉrvénytelen menüpont!")

    def after_action_menu(self, next_menu=None, menu_name ="Főmenü megjelenítése"):
        print("\n------------------------------")
        print(f"    (1) {menu_name}")
        print("    (0) Kilépés a programból")
        print("------------------------------\n")

        while True:
            choice = input("Választott menü: ").strip()

            if choice == "1":
                if next_menu:
                    next_menu.show()
                return

            elif choice == "0":
                self.exit_app()

            else:
                print("Érvénytelen választás!")

    @staticmethod
    def exit_app():
        print("Kilépés...")
        sys.exit(0)
