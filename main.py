import csv
import json
import random
import sys
import time

import capsolver
import requests

from utils.logger import CustomLogger
from utils.save_to_csv import save_success_data
from utils.webhooks import Webhook

log = CustomLogger(__name__)


class Account:
    proxy = []
    fingerprint = ["5f365f6da776a4ebdb2c5f8ea8d1a68d", "1b7e1b5a9cd9931c61c028b2de59b10f",
                    "a11a1b233f8a6e9f71c93c7521a329ab", "c3b47470daa0c9a7394824ea12cfd5d1",
                    "899b821f0a8cd6dbb8b43f671df5d781", "3d8783156630ccfe0cc7e599e5e0475c",
                    "bddc398d5d34994d2e8e6b5083ea8da6", "19a7e8985c44b8ee2dca970fc8520122",
                    "e1ca82b3e8efc26f6f846d7082c8d9bc", "77b554de4407974ba69e1f6775b416b7",
                    "fac8cb2ad4ce55760dc41a9301f47f7b", "0418201bb96e8b6efc2446ba6dd5fe6b"]

    def __init__(self, data):
        self.data = data
        self.session = requests.Session()
        self.mail = f"{self.data['login']}@{self.data['domain']}"

    @classmethod
    def proxy_format(cls):
        try:
            with open("proxies.txt", "r") as file:
                proxy_lines = (line.strip().split(":") for line in file)
                cls.proxy.extend([f"http://{octet[2]}:{octet[3]}@{octet[0]}:{octet[1]}" for octet in proxy_lines])

            if not cls.proxy:
                raise ValueError("Fill proxies.txt file")

        except ValueError as e:
            log.error(e)
            sys.exit()
        except Exception as e:
            log.error(e)
            sys.exit()

    @classmethod
    def get_capsvoler_key(cls):
        try:
            with open("key.json", "r") as file:
                data = json.load(file)

                if not data['key']:
                    log.error("Add capsolver key in key.json")
                    sys.exit()
                capsolver.api_key = data['key']
        except Exception as e:
            log.error(e)
            sys.exit()

    @staticmethod
    def generate_date():
        return f"{random.choice(range(1990, 2003))}-{str(random.choice(range(1, 13))).zfill(2)}-{str(random.choice(range(1, 30))).zfill(2)}"

    def first_payload(self):
        try:
            log.debug(f"[{self.mail}]Solving ReCaptcha...")

            self.solution = capsolver.solve({
                "type": "ReCaptchaV3Task",
                "pageAction": "checkRegisterEmailIdentity",
                "websiteKey": "6LcdGIQlAAAAAHWCwQXSx1-Voi9npxOU9zNiwGdz",
                "websiteURL": "https://konto.onet.pl/register?state=https%3A%2F%2Fpoczta.onet.pl%2F&client_id=poczta.onet.pl.front.onetapi.pl",
                "proxy": random.choice(Account.proxy)
            })

            log.debug(f"[{self.mail}]Submitting payload...")

            req = self.session.post(
                "https://konto.onet.pl/newapi/oauth/check-register-email-identity",
                headers={
                    "content-type": "application/json",
                    "referer": "https://konto.onet.pl/",
                    "user-agent": self.solution['userAgent']
                },
                data=json.dumps({
                    "state": "https://poczta.onet.pl/",
                    "login": self.data['login'],
                    "domain": self.data['domain'],
                    "captcha_response": self.solution['gRecaptchaResponse'],
                }),
                proxies={
                    "https": random.choice(Account.proxy)
                },
                timeout=7)

            if req.ok:
                try:
                    if req.json()['verificationType'] == 'CAPTCHA':
                        time.sleep(1)
                        self.second_payload()
                    elif req.json()['verificationType'] == 'SMS':
                        log.critical(f"[{self.mail}]Account requires phone number verification, retrying in 10 seconds...")
                        time.sleep(10)
                        return self.first_payload()
                except Exception as e:
                    log.error(f"[{self.mail}]Unknown error [{req.status_code} | {e}]")
                    time.sleep(5)
                    return self.first_payload()
        except requests.exceptions.ProxyError:
            log.error(f"[{self.mail}]Proxy Error, retrying in 5 seconds...")
            time.sleep(5)
            return self.first_payload()
        except requests.exceptions.Timeout:
            log.error(f"[{self.mail}]Timeout, retrying in 5 seconds...")
            time.sleep(5)
            return self.first_payload()

    def second_payload(self):
        try:
            log.debug(f"[{self.mail}]Creating account...")

            req = self.session.post(
                "https://konto.onet.pl/newapi/oauth/email-user",
                headers={
                    "content-type": "application/json",
                    "referer": "https://konto.onet.pl/",
                    "user-agent": self.solution['userAgent']
                },
                data=json.dumps({
                    "login": self.data['login'],
                    "domain": self.data['domain'],
                    "password": self.data['password'],
                    "name": self.data['firstname'],
                    "surname": self.data['lastname'],
                    "place": None,
                    "postal_code": None,
                    "sex": "M",
                    "date_of_birth": Account.generate_date(),
                    "agreements": ["6", "21", "85"],
                    "phone": "",
                    "phone_token": None,
                    "fingerprint": random.choice(Account.fingerprint),
                    "browser_params": self.solution['userAgent'],
                    "guardian_email": "",
                    "save_phone": True,
                    "client_id": "poczta.onet.pl.front.onetapi.pl",
                    "recoveryEmail": self.data['recovery mail'],
                    "lang": "pl",
                    "group_order": "",
                    "service_with_inbox": False
                }))

            if req.ok:
                if "https://konto.onet.pl/checkSSO/auth.html?client_id=poczta.onet.pl.front.onetapi.pl&code=" in req.json()['redirectUrl']:
                    log.info(f"[{self.mail}]Account created!")
                    save_success_data(self.data)
                    Webhook.onet_success(
                        self.data['webhook url'],
                        f"{self.mail}:{self.data['password']}"
                    )
                else:
                    log.error(f"[{self.mail}]Something went wrong while creating account... [{req.json()}]")
                    Webhook.onet_failed(
                        self.data['webhook url'],
                        f"{self.mail}:{self.data['password']}",
                        f"Something went wrong while creating account [{req.json()}]"
                    )
            elif req.status_code == 500:
                log.error(f"[{self.mail}]Incorrect data in the csv file/fingerprint")
                Webhook.onet_failed(
                    self.data['webhook url'],
                    f"{self.mail}:{self.data['password']}",
                    f"Incorrect data in the csv file/fingerprint"
                )
        except requests.exceptions.ProxyError:
            log.error(f"[{self.mail}]Proxy Error, retrying in 5 seconds...")
            time.sleep(5)
            return self.second_payload()
        except requests.exceptions.Timeout:
            log.error(f"[{self.mail}]Timeout, retrying in 5 seconds...")
            time.sleep(5)
            return self.second_payload()


def run():
    Account.proxy_format()
    Account.get_capsvoler_key()

    with open('data/onet.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        lines = list(reader)


    for i in lines:
        if all(value for value in i.values()):
            task = Account(i)
            task.first_payload()
            log.warning("Waiting 30 seconds...")
            time.sleep(30)
        else:
            log.error("Missing value(s) in csv line, skipping...")
            time.sleep(3)

    print("", flush=True)

    log.info("ALL TASKS HAS BEEN EXECUTED")


if __name__ == '__main__':
    run()
