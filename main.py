import telebot
from utils import transaction_process, show_bal, transaction_record, register_user, mark_as_done
import pandas as pd

bot = telebot.TeleBot("7204964331:AAGcJe-_-EMhYEtEIQYxkwIfkI509vC5s68")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello, this is bookkeeping bot!\nAll of users should send /register so that I can remember you")
    bot.reply_to(message, "Use /help to see how to use.")

@bot.message_handler(commands=['register'])
def register(message):
    bot.reply_to(message, register_user(message))

@bot.message_handler(commands=['help'])
def get_info(message):
    text = "/register: Register as a bookkeeping bot user\n\n"
    text = text + "/add: Add a transaction in the format /add @user1 @user2 [Amount] [Memo(optional)]\n\n"
    text = text + "/bal: Check a pair of users' balance in the format /bal @user1 @user2\n\n"
    text = text + "/rec: Check the past n days transaction record in the format /rec @user1 @user2 [n]\n\n"
    text = text + "/delete: Delete a pair of users' transaction record in the format /delete @user1 @user2"
    bot.reply_to(message, text)

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
