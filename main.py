from bot import bot
from db import session, User, Transaction
from utils import transaction_process, show_bal, transaction_record, register_user, mark_as_done
import pandas as pd

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello, this is bookkeeping bot!\nAll of users should send /register so that I can remember you")
    bot.reply_to(message, "Use /help to see how to use.")

@bot.message_handler(commands=['register'])
def register(message):
    bot.reply_to(message, register_user(message))

@bot.message_handler(commands=['help'])
def get_info(message):
    bot.reply_to(message,"/register: register as a bookkeeping bot user\n/add: add a transaction\n/bal: make a query of the balance of two people")

@bot.message_handler(commands=['add'])
def enter_transaction(message):
    bot.reply_to(message, transaction_process(message))

@bot.message_handler(commands=['bal'])
def bal_query(message):
    bot.reply_to(message, show_bal(message))

@bot.message_handler(commands=['rec'])
def trans_record(message):
    bot.reply_to(message, transaction_record(message))

@bot.message_handler(commands=['delete'])
def delete_rec(message):
    bot.reply_to(message, mark_as_done(message))

bot.infinity_polling()
