import json
import smtplib
from email.mime.text import MIMEText

import requests as requests
from flask import Flask, request, Response
from user import User

app = Flask(__name__)
env = json.load(open("env.json"))


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/register-devhacks-2024', methods=["POST"])
def register():
    full_form_data = request.get_json()  # Webhook Data
    questions = full_form_data["data"]["fields"]  # Create QUestions

    # Create User
    attendee = User()
    attendee.first_name = questions[0]["value"]
    attendee.last_name = questions[1]["value"]
    attendee.preferred_name = questions[2]["value"]
    attendee.email = questions[5]["value"]

    # Create Ticket
    ticket_info = add_to_ticket_tailor(attendee)
    send_to_discord(attendee, info)
    if ticket_info:
        send_email(attendee, info)
        return "Successfully Created Ticket", 201
    else:
        return "Failed to Create Ticket", 503


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

    status = str(r.status_code)[0] == "2"
    if not status:
        ret = None
    else:
        ret = r.json()
    return ret


def send_to_discord(attendee, ticket_info=None):
    url = env.get("discord_webhook_url")
    header = {
        "Accept": "application/json"
    }
    if ticket_info:
        body = {
            "content": f"{attendee.first_name} {attendee.last_name} has registered!\n"
                       f"Email: `{attendee.email}`\n"
                       f"Ticket Number: `{ticket_info['id']}`\n"
                       f"Ticket Barcode: [link]({ticket_info['qr_code_url']})"
        }
    else:
        body = {
            "content": f"WARNING: {attendee.first_name} {attendee.last_name} tried to register, "
                       f"but something went wrong.\nEmail: `{attendee.email}`"
        }
    r = requests.post(url, headers=header, data=body)
    print(f"{r.status_code} {r.reason}")


def send_email(attendee, ticket_info):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login('umdevclub@gmail.com', env.get("gmail_pass"))

    content = open("ticket_email.html", "r").read()
    content = content.format(
        styles=open("styles.css", 'r').read(),
        preferred_name=attendee.preferred_name if attendee.preferred_name else attendee.first_name,
        ticket_qr=ticket_info.get("qr_code_url"),
        ticket_code=ticket_info.get("barcode"),
        ticket_type=ticket_info.get("description")
    )

    message = MIMEText(content, 'html')
    message["Subject"] = ".devHacks 2024 Ticket"
    message["From"] = "umdevclub@gmail.com"
    message["To"] = attendee.email

    s.sendmail("umdevclub@gmail.com", attendee.email, message.as_string())


if __name__ == '__main__':
    # app.run()
    att = User(first_name="Test", last_name="User", email="khathepham@gmail.com")
    info = json.load(open("test_ticket.json"))
    # send_to_discord(att, info)
    send_email(att, info)
