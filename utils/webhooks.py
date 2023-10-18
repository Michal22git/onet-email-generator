from datetime import datetime

import requests


class Webhook:
    @staticmethod
    def onet_success(webhook_url, login):
        requests.post(
            webhook_url,
            json={"embeds": [
                {
                    "title": "EMAIL WAS CREATED",
                    "description": f"[Login url](https://konto.onet.pl/checkSSO/login.html?client_id=poczta.onet.pl.front.onetapi.pl&state=https://poczta.onet.pl/)",
                    "color": 48995,
                    "fields": [
                        {
                            "name": "Login:",
                            "value": f"```{login}```",
                            "inline": True
                        }
                    ],
                    "footer": {
                        "text": f"Onet email gen | {datetime.now().strftime('%H:%M:%S.%f')}",
                    },
                },
            ]}
        )

    @staticmethod
    def onet_failed(webhook_url, login, error):
        requests.post(
            webhook_url,
            json={"embeds": [
                {
                    "title": "FAILED TO CREATE EMAIL",
                    "color": 16711680,
                    "fields": [
                        {
                            "name": "Login:",
                            "value": f"```{login}```",
                            "inline": False
                        },
                        {
                            "name": "Error:",
                            "value": error,
                            "inline": False
                        }
                    ],
                    "footer": {
                        "text": f"Onet email gen | {datetime.now().strftime('%H:%M:%S.%f')}",
                    },
                },
            ]}
        )
