class Attendee:
    def __init__(self, first_name=None, last_name=None, preferred_name=None, email=None,
                 phone_number=None, obj=None, ticket_id=None, school_email=None):
        if obj:
            self.from_obj(obj)
        else:
            self.first_name = first_name
            self.last_name = last_name
            self.preferred_name = preferred_name
            self.email = email
            self.school_email = school_email
            self.phone_number = phone_number
            self.discord_name = None
            self.ticket_id = ticket_id

    def to_obj(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "preferred_name": self.preferred_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "discord_name": self.discord_name
        }

    def from_obj(self, obj):
        self.first_name = obj.get("first_name")
        self.last_name = obj.get("last_name")
        self.preferred_name = obj.get("preferred_name")
        self.email = obj.get("email")
        self.phone_number = obj.get("phone_number")
        self.discord_name = obj.get("discord_name")
