# from django.conf import settings
from twilio.rest import Client
from accounts.otp_verification.secure import accont_sid,host_number,auth_token
class MessageHandler:
    phone_number = None
    otp = None
    def __init__(self, phone_number, otp):
        self.phone_number = phone_number
        self.otp = otp
    
    
    def send_otp_to_phone(self):
        client  = Client(accont_sid, auth_token)
        message = client.messages.create(
            body = f"\nHi, \n{self.otp} is the otp for your HarmonicHut account. Please don't share it with anyone.",
            from_ = host_number,
            to = self.phone_number
        )