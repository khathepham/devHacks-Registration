import json
import subprocess
import time

import requests
import js2py

env = json.load(open("env.json"))
timeout = 1


def checkin(ticket_id):
    ticket = get_ticket(ticket_id)

    rate_limited = True

    if ticket:
        checked_in = ticket["properties"]["Checked In"]["checkbox"]
        first_name = ticket['properties']['First Name']['rich_text'][0]['plain_text']
        last_name = ticket['properties']['Last Name']['rich_text'][0]['plain_text']

        if not checked_in:
            while rate_limited:
                notion_auth = env["notion_pass"]
                completed_process = subprocess.run(["node", "../test.js", notion_auth, ticket["id"]],
                                                   capture_output=True)
                r = completed_process.stdout.decode()
                r = json.loads(r)

                if r["object"] and not r["object"] == "error":
                    print(json.dumps(r, indent=4, sort_keys=True))
                    print(f"Successfully checked in {first_name} {last_name} with ticket {ticket_id}!")
                    rate_limited = False
                elif r.get("object") == "error" and r.get("status") == 429:
                    print(f"Rate Limited - Retrying in {timeout} second(s)...")
                    time.sleep(timeout)
                else:
                    print(
                        f"Something went wrong trying to check in {first_name} {last_name} - {r.get('status', 400)} {r.get('message', '')}")
                    rate_limited = False
        else:
            print(f"{first_name} {last_name} is already checked in!")


def get_ticket(ticket_id):
    notion_auth = env["notion_pass"]
    notion_db = env["notion_database"]
    url = f"https://api.notion.com/v1/databases/{notion_db}/query"
    body = {
        "filter": {
            property: "%7CFWd",
            "rich_text": {
                "equals": ticket_id
            }
        },
        "page_size": 1
    }
    header = {
        "Authorization": f"Bearer {notion_auth}",
        "Notion-Version": "2022-06-28"
    }

    while True:
        r = requests.post(url, headers=header, data=body)
        if r.status_code == 200:
            return r.json().get("results", [None])[0]
        elif r.status_code == 429:
            wait_time = r.headers.get("Retry-After")
            time.sleep(wait_time)
        else:
            return None


if __name__ == '__main__':
    checkin("9vL50X")
