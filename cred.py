import os

#Twilio Details
account_sid = os.environ.get('ACCOUNT_SID')
auth_token = os.environ.get('AUTH_TOKEN')
twilionumber = os.environ.get('TWILIO_NUMBER')
twiliosmsnumber = os.environ.get('TWILIO_SMS_NUMBER')

#FC Bot
API_TOKEN = os.environ.get('API_TOKEN')

#Host URL
callurl = os.environ.get('CALL_URL')
twiliosmsurl = os.environ.get('TWILIO_SMS_URL')
