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
            attendee.email = questions[5]["value"]

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
    qr.save(b, kind="png", scale=4)
    return Response(b.read(), mimetype='image/png')


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
                       f"Ticket Barcode: [link](https://devhacks2024.khathepham.com/{url_for('qr_code', ticket_id=attendee.ticket_id)}.png)"
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

    with open("./static/styles/style.css", "r") as fil:
        css = fil.read()

    content = render_template("email.html", attendee=attendee, css=css)

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
