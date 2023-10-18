import csv

from utils.logger import CustomLogger

log = CustomLogger(__name__)


def save_success_data(data):
    try:
        with open('data/created_accounts.csv', 'a', newline='') as file:
            fieldnames = ['login', 'password', 'firstname', 'lastname', 'recovery mail']
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if file.tell() == 0:
                writer.writeheader()

            writer.writerow({'login': f"{data['login']}@{data['domain']}", 'password': data['password'], 'firstname': data['firstname'], 'lastname': data['lastname'], 'recovery mail': data['recovery mail']})
    except Exception as e:
        log.error(f"Failed to save data [{e}]")
