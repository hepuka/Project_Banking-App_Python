import random

class Helpers:

    @staticmethod
    def generate_account_number(account_type):
        starter = "1177" if account_type == "HUN" else "2255"
        first_block = starter + str(random.randint(1000, 9999))
        second_block = str(random.randint(10_000_000, 99_999_999))
        third_block = str(random.randint(10_000_000, 99_999_999))
        return f"{first_block}-{second_block}-{third_block}"

    @staticmethod
    def format_amount(amount) -> str:
        return f"{int(round(amount)):,}".replace(",", ".")

    @staticmethod
    def print_table(title: str, rows: list[tuple[str, str]]):
        col_width = max(len(label) for label, _ in rows) + 2

        print(f"\n{title}")

        for label, value in rows:
            print(f"{label.ljust(col_width)} | {value}")

    @staticmethod
    def get_positive_int(prompt: str) -> int:
        value = input(prompt).strip()
        if not value.isdigit():
            raise ValueError("Pozitív szám szükséges.")
        return int(value)

    @staticmethod
    def _validate_positive_amount(amount: int):
        if amount <= 0:
            raise ValueError("Az összegnek pozitívnak kell lennie!")

