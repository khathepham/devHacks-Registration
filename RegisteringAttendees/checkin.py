import json
import subprocess
import time

import requests
import js2py
from enum import Enum

env = json.load(open("./env.json"))
timeout = 1


class Day(Enum):
    FRIDAY = "Friday"
    SATURDAY = "Saturday"

class Meal(Enum):
    LUNCH = "Lunch"
    DINNER = "Dinner"


def checkin(ticket_id: str, day: Day):
    ticket = get_ticket(ticket_id)

    rate_limited = True

    return_val = {"success": False}

    if ticket:
        return_val["ticket"] = ticket
        checked_in = ticket["properties"][f"Checked In - {day.value}"]["checkbox"]
        first_name = ticket['properties']['First Name']['rich_text'][0]['plain_text']
        last_name = ticket['properties']['Last Name']['rich_text'][0]['plain_text']

        if not checked_in:
            while rate_limited:
                r = checkin_notion_request(ticket["id"], day)

                if r["object"] and not r["object"] == "error":
                    print(json.dumps(r, indent=4, sort_keys=True))
                    print(f"Successfully checked in {first_name} {last_name} with ticket {ticket_id}!")
                    return_val[
                        "status"] = f"Successfully checked in {first_name} {last_name} with ticket {ticket_id} for {day.value}!"
                    return_val["success"] = True
                    rate_limited = False
                elif r.get("object") == "error" and r.get("status") == 429:
                    print(f"Rate Limited - Retrying in {timeout} second(s)...")
                    time.sleep(timeout)
                else:
                    print(
                        f"Something went wrong trying to check in {first_name} {last_name} - {r.get('status', 400)} {r.get('message', '')}")
                    return_val[
                        "status"] = f"Something went wrong trying to check in {first_name} {last_name} - {r.get('status', 400)} {r.get('message', '')}!"

                    rate_limited = False
        else:
            return_val["status"] = f"{first_name} {last_name} is already checked in on {day.value}!"
            print(f"{first_name} {last_name} is already checked in!")
    else:
        return_val["status"] = f"{ticket_id} is an invalid ticket code. Please check with the Notion Page."
        return_val["ticket"] = None
    return return_val


def meal_checkin(ticket_id: str, day: Day, meal: Meal, meal_groups):
    ticket = get_ticket(ticket_id)
    rate_limited = True
    return_val = {"success": False, "warning": False}

    if not ticket:
        return_val["status"] = f"{ticket_id} is an invalid ticket code. Please check with the Notion Page."
        return_val["ticket"] = None
    else:
        return_val["ticket"] = ticket
        checked_in = ticket["properties"][f"{day.value} {meal.value} Redeemed"]["checkbox"]
        first_name = ticket['properties']['First Name']['rich_text'][0]['plain_text']
        last_name = ticket['properties']['Last Name']['rich_text'][0]['plain_text']

        if checked_in:
            return_val["status"] = f"{first_name} {last_name} has already claimed {day.value} {meal.value}!"
            print(f"{first_name} {last_name} has already claimed {day.value} {meal.value}")
        else:
            while rate_limited:
                if ticket['properties']['Meal Group']['select'] is None:
                    return_val["status"] = (f"{first_name} {last_name} has not been placed in a meal group, as they "
                                            f"are not registered in any .devHacks team. Please notify ticket-holder "
                                            f"that they must be an active participant of .devHacks "
                                            f"for food during the event.")
                    return_val["warning"] = True
                    rate_limited = False
                elif not correct_meal_group(ticket, meal_groups):
                    return_val["status"] = (f"{first_name} {last_name} is not in this meal group. Please ask them to "
                                            f"wait until their group "
                                            f"(Group {ticket['properties']['Meal Group']['select']['name']})"
                                            f" is called.")
                    return_val["warning"] = True
                    rate_limited = False
                else:
                    r = checkin_meal_notion_request(ticket["id"], day, meal)

                    if r["object"] and not r["object"] == "error":
                        print(json.dumps(r, indent=4, sort_keys=True))
                        print(f"Successfully redeemed {first_name} {last_name} with ticket {ticket_id}!")
                        return_val[
                            "status"] = f"Successfully redeemed {first_name} {last_name} with ticket {ticket_id} for {day.value} {meal.value}!"
                        return_val["success"] = True
                        rate_limited = False
                    elif r.get("object") == "error" and r.get("status") == 429:
                        print(f"Rate Limited - Retrying in {timeout} second(s)...")
                        time.sleep(timeout)
                    else:
                        print(
                            f"Something went wrong trying to check in {first_name} {last_name} - {r.get('status', 400)} {r.get('message', '')}")
                        return_val[
                            "status"] = f"Something went wrong trying to redeem {first_name} {last_name} - {r.get('status', 400)} {r.get('message', '')}!"

                        rate_limited = False
    return return_val


def correct_meal_group(attendee, meal_groups):
    if attendee["properties"]["Meal Group"]["select"] is not None:
        return attendee["properties"]["Meal Group"]["select"]["name"] in meal_groups
    return False


def checkin_notion_request(page_id, day):
    notion_auth = env["notion_pass"]
    url = f"https://api.notion.com/v1/pages/{page_id}"
    body = {
        "properties": {
            f"Checked In - {day.value}": True
        }
    }
    header = {
        "Authorization": f"Bearer {notion_auth}",
        "Notion-Version": "2022-06-28"
    }

    r = requests.patch(url, json=body, headers=header)
    data = r.json()
    return data


def checkin_meal_notion_request(page_id, day, meal):
    notion_auth = env["notion_pass"]
    url = f"https://api.notion.com/v1/pages/{page_id}"
    body = {
        "properties": {
            f"{day.value} {meal.value} Redeemed": True
        }
    }
    header = {
        "Authorization": f"Bearer {notion_auth}",
        "Notion-Version": "2022-06-28"
    }

    r = requests.patch(url, json=body, headers=header)
    data = r.json()
    return data


def get_ticket(ticket_id):
    notion_auth = env["notion_pass"]
    notion_db = env["notion_database"]
    url = f"https://api.notion.com/v1/databases/{notion_db}/query"
    body = {
        "filter": {
            "property": "Ticket ID",
            "rich_text": {
                "contains": ticket_id
            }
        },
        "page_size": 1
    }
    header = {
        "Authorization": f"Bearer {notion_auth}",
        "Notion-Version": "2022-06-28"
    }

    while True:
        r = requests.post(url, headers=header, json=body)
        if r.status_code == 200:
            data = r.json().get("results", [None])
            if len(data) == 0:
                return None
            return data[0]
        elif r.status_code == 429:
            wait_time = r.headers.get("Retry-After")
            time.sleep(wait_time)
        else:
            return None


if __name__ == '__main__':
    checkin("p7e9qB", Day.FRIDAY)
