# from django.conf import settings
from twilio.rest import Client
from decouple import config
from django.conf import settings

class MessageHandler:
    phone_number = None
    otp = None
    def __init__(self, phone_number, otp):
        self.phone_number = phone_number
        self.otp = otp
    
    
    def send_otp_to_phone(self):
        client  = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
        message = client.messages.create(
            body = f"\nHi, \n{self.otp} is the otp for your HarmonicHut account. Please don't share it with anyone.",
            from_ = settings.HOST_NUMBER,
            to = self.phone_number
        )