import json

from notion.client import NotionClient
env = json.load(open("env.json"))


def resend_email():
    client = NotionClient(token_v2="e7Gii5h7wPaCUqf8Xx7Cd3kHikrzNcfrmOtqUwt3eWqla8ai37za46Gkc5x2zXdQsowiAx5vR63LPR5PvyVhejjhgB57BcxiaqpnkTRV4NL22IXzs61GTIUTf6W3s")
    db = client.get_collection(env.get("notion_database"))
    result = db.get_rows()
    for row in result:
        if row.resend_ticket:
            print(f"Resending Ticket to {row.preferred_name} at {row.preferred_email if row.preferred_email else row.school_email}")


if __name__ == '__main__':
    resend_email()