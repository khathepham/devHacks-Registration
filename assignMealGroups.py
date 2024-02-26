import csv
import json
import threading

import requests

import RegisteringAttendees.checkin as checkinUtils

env = json.load(open("env.json"))
def assignMealGroups():
    all_registered_teams = all_teams()

    for team in all_registered_teams:
        for member in team["members"]:
            if member:
                threading.Thread(target=assignAttendees, args=(member, team)).start()
                print(f"Starting Thread for {member}")



def assignAttendees(member, team):
    attendee = checkinUtils.get_ticket(member)
    if attendee is not None:
        meal_group = team["meal_group"]
        if len(attendee["properties"]["Dietary Restrictions"]["multi_select"]) > 1 or \
                attendee["properties"]["Dietary Restrictions"]["multi_select"][0]["name"] != "None":
            meal_group = "DR"
        assignMealGroupAndTeam(attendee["id"], meal_group, team["team_name"])
        # print(f"Added {meal_group}, {team['team_name']} to {member}")
    else:
        print(f"Ticket {member} not found.")
def assignMealGroupAndTeam(ticket_uuid, meal_group, team):
    notion_auth = env["notion_pass"]
    url = f"https://api.notion.com/v1/pages/{ticket_uuid}"
    body = {
        "properties": {
            "Meal Group": {
                "select": {
                    "name": meal_group
                }
            },
            "Team": {
                "select": {
                    "name": team
                }
            }
        }
    }
    header = {
        "Authorization": f"Bearer {notion_auth}",
        "Notion-Version": "2022-06-28"
    }

    r = requests.patch(url, json=body, headers=header)
    data = r.json()
    return data



def all_teams():
    teams = []
    with open('devHacks 2024 Team Assignments, Internal - Sheet1.csv', mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            team = {
                "meal_group": row["Meal Group"],
                "team_name": row["Team Name"],
                "members": [
                    row["Person 1 Ticket Code"],
                    row["Person 2 Ticket Code"],
                    row["Person 3 Ticket Code"],
                    row["Person 4 Ticket Code"],
                    row["Person 5 Ticket Code"]
                ]
            }
            teams.append(team)
    return teams


if __name__ == '__main__':
    assignMealGroups()
