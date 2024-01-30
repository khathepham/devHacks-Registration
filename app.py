import json

import requests as requests
from flask import Flask, request
from user import User

app = Flask(__name__)
env = json.load(open("env.json"))


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/register-devhacks-2024', methods=["POST"])
def register():
    full_form_data = request.get_json()
    questions = full_form_data["data"]["fields"]
    attendee = User()
    attendee.first_name = questions[0]["value"]
    attendee.last_name = questions[1]["value"]
    attendee.preferred_name = questions[2]["value"]
    attendee.email = questions[3]["value"]


def add_to_ticket_tailor(attendee: User):
    url = "https://api.tickettailor.com/v1/issued_tickets"
    body = {
        "event_id": env.get("event_id"),
        "ticket_type_id": env.get("ticket_type_id"),
        "email": attendee.email,
        "full_name": f"{attendee.first_name} {attendee.last_name}"
    }
    header = {
        "Accept": "application/json"
    }
    r = requests.post(url, headers=header, auth=(env.get('tt_key'), ''), data=body)
    print(f"{r.status_code} {r.reason}")
    print(json.dumps(r.json(), indent=4))


if __name__ == '__main__':
    # app.run()
    att = User(first_name="Test", last_name="User", email="khathepham@gmail.com")
    add_to_ticket_tailor(att)
