from repositories.account_repository import AccountRepository

class AccountService:

    @staticmethod
    def deposit(c, account, amount):
        account.deposit(c, amount)
        AccountRepository.save(account)

    @staticmethod
    def withdraw(c, account, amount, cost):
        account.withdraw(c, amount, cost)
        AccountRepository.save(account)

    @staticmethod
    def transfer(source_customer, source_account, target_account, amount, cost):
        # csak az account objektumokat és a customer objektumot adjuk át
        source_account.transfer_to(
            target_account,
            amount,
            cost,
            source_customer.id  # a tranzakcióhoz szükséges küldő id
        )

        AccountRepository.save(source_account)
        AccountRepository.save(target_account)



