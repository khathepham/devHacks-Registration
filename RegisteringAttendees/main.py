import json
import os
import smtplib
import sys
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
import io
import jinja2

from os.path import basename

import requests as requests
import segno
from flask import Flask, request, Response, url_for, render_template
from attendee import Attendee

app = Flask(__name__)
env = json.load(open("env.json"))


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/register-devhacks-2024', methods=["POST"])
def register():
    full_form_data = request.get_json()  # Webhook Data
    r = create_and_send_ticket(full_form_data)
    print(r)
    return r


def create_and_send_ticket(full_form_data):
    try:

        questions = full_form_data["data"]["fields"]  # Create QUestions

        # Create User
        attendee = Attendee()
        attendee.first_name = questions[0]["value"]
        attendee.last_name = questions[1]["value"]
        attendee.preferred_name = questions[2]["value"]
        attendee.school_email = questions[3]["value"]
        attendee.ticket_id = full_form_data["data"]["responseId"]

        if questions[4]["value"]:
            attendee.email = attendee.school_email
        else:
            attendee.email = questions[6]["value"]

        # Create Ticket
        send_to_discord(attendee)

        send_email(attendee)
        return "Successfully Created Ticket", 201

    except KeyboardInterrupt as k:
        print("Ending the Program")
        sys.exit(0)
    except Exception as e:
        print(e)
        traceback.print_exception(e)
        return "Something went Wrong", 503


@app.route('/register-devhacks-2024/<ticket_id>', methods=["GET"])
def qr_code(ticket_id):
    qr = segno.make_qr(ticket_id)
    b = io.BytesIO()
    qr.save(b, kind="png", scale=6)
    return Response(b.getvalue(), mimetype='image/png')


@app.route('/register-devhacks-2024/resend_email/<notion_page_id>', methods=["POST"])
def resend_email(notion_page_id):
    notion_auth = env.get("notion_pass")
    url = f"https://api.notion.com/v1/pages/{notion_page_id}"
    header = {
        "Authorization": f"Bearer {notion_auth}",
        "Notion-Version": "2022-06-28"
    }
    r = requests.get(url, headers=header)
    print(json.dumps(r.json(), indent=4))
    if r.status_code == 404:
        return "404 ID Not Found", 404
    elif r.status_code == 400 or r.status_code == 429:
        return "429 Rate Limited"
    else:
        info = r.json().get("properties")
        attendee = Attendee()
        attendee.first_name = info.get("First Name").get("rich_text")[0].get("plain_text")
        attendee.last_name = info.get("Last Name").get("rich_text")[0].get("plain_text")
        attendee.ticket_id = info.get("Ticket ID").get("title")[0].get("plain_text")
        attendee.school_email = info.get("School Email").get("email")
        attendee.email = info.get("Preferred Email").get("email")
        if not attendee.email:
            attendee.email = attendee.school_email
        preferred_name = info.get("Preferred Name").get("rich_text", [])
        preferred_name = None if len(preferred_name) == 0 else preferred_name[0].get("plain_text")
        attendee.preferred_name = preferred_name;

        send_email(attendee)
        return "Successfully Sent Email", 200


def send_to_discord(attendee):
    url = env.get("discord_webhook_url")
    header = {
        "Accept": "application/json"
    }
    if attendee.ticket_id:
        body = {
            "content": f"{attendee.first_name} {attendee.last_name} has registered!\n"
                       f"Email: `{attendee.email}`\n"
                       f"Ticket Number: `{attendee.ticket_id}`\n"
                       f"Ticket Barcode: [link](https://devhacks2024.khathepham.com{url_for('qr_code', ticket_id=attendee.ticket_id)}.png)"
        }
    else:
        body = {
            "content": f"WARNING: {attendee.first_name} {attendee.last_name} tried to register, "
                       f"but something went wrong.\nEmail: `{attendee.email}`"
        }
    r = requests.post(url, headers=header, data=body)
    print(f"{r.status_code} {r.reason}")


def send_email(attendee):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login('umdevclub@gmail.com', env.get("gmail_pass"))

    with open("static/styles/style.css", "r") as fil:
        css = fil.read()

    with open("templates/email.html", 'r') as f:
        text = f.read()
        template = jinja2.Template(text)
    content = template.render(attendee=attendee, css=css)

    message = MIMEMultipart()
    message.attach(MIMEText(content, 'html'))
    message["Subject"] = f".devHacks 2024 Ticket - {attendee.ticket_id}"
    message["From"] = "umdevclub@gmail.com"
    message["To"] = attendee.email

    qr = attendee.ticket_qr()
    b = io.BytesIO()
    qr.save(b, kind="png", scale=6)

    image = MIMEImage(b.getvalue(), Name=f"{attendee.ticket_id}.png", _subtype="png")
    image.add_header('Content-ID', attendee.ticket_id)
    message.attach(image)
    s.sendmail("umdevclub@gmail.com", attendee.email, message.as_string())


if __name__ == '__main__':
    app.run()
    # ticket = json.load(open("./test_ticket.json", 'r'))
    # create_and_send_ticket(ticket)
    # send_email(att, info)
    # resend_email("6ed8d453-ee3b-465d-99c7-06ccd9d14e9a")
