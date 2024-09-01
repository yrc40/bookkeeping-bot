import telebot
from db import session, User, Transaction
import pandas as pd

bot = telebot.TeleBot("7204964331:AAGcJe-_-EMhYEtEIQYxkwIfkI509vC5s68")

n = 0
names = []

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello, this is bookkeeping bot!\nAll of users should send /register so that I can remember you")
    bot.reply_to(message, "Use /info to see how to use.")

@bot.message_handler(commands=['register'])
def register_user(message):
    user_id = message.from_user.id
    username = message.from_user.username
    existing_user = session.query(User).filter_by(id=user_id).first()

    if existing_user is None:
        user_data = User(id=user_id, name=username)
        session.add(user_data) 
        session.commit()
        bot.reply_to(message, f"Hi, @{username}. You are registered successfully.")
    else:
        bot.reply_to(message,f"User already exists: ID = {user_id}, Username = {username}")

@bot.message_handler(commands=['info'])
def get_info(message):
    bot.reply_to(message,"/register: register as a bookkeeping bot user\n/add: add a transaction\n/bal: make a query of the balance of two people")

@bot.message_handler(commands=['add'])
def enter_transaction(message):
    bot.reply_to(message, "Enter a transaction in this format: [sender] [receiver] [amount]")
    bot.register_next_step_handler(message, transaction_process)

def transaction_process(message):
    trans = message.text.split()
    sender = trans[0]
    receiver = trans[1]
    amount = float(trans[2])
    if not amount > 0:
        bot.reply_to(message, "Invalid transaction amount, please enter the transcation again")
        bot.register_next_step_handler(message, enter_transaction)
    else:
        table = pd.read_csv("user_table.csv", index_col = 0)
        if sender in table.index and receiver in table.columns:
            table.at[sender, receiver] += amount
            table.to_csv("user_table.csv", index = True)
            bot.reply_to(message, f"Transaction of {amount} from {sender} to {receiver} recorded.")
        else:
            bot.reply_to(message, "Invalid sender or receiver. Please enter the transaction again.")
            bot.register_next_step_handler(message, enter_transaction)

@bot.message_handler(commands=['bal'])
def bal_query(message):
    bot.reply_to(message, "Enter a pair of user to look up balance: [user1] [user 2]")
    bot.register_next_step_handler(message, show_bal)

def show_bal(message):
    user = message.text.split()
    user1 = user[0]
    user2 = user[1]
    table = pd.read_csv("user_table.csv", index_col = 0)
    if not user1 == user2 and user1 in table.index and user2 in table.index:
        m12 = table.at[user1, user2]
        m21 = table.at[user2, user1]
        if(m12 >= m21):
            bot.reply_to(message, f"*--- Balance of {user1} and {user2} ---*\n{user2} should give {user1} {m12-m21}")
        else:
            bot.reply_to(message, f"*--- Balance of {user1} and {user2} ---*\n{user1} should give {user2} {m21-m12}")
    else:
        bot.reply_to(message, "Invalid query. Please enter users again")
        bot.register_next_step_handler(message, bal_query)







bot.infinity_polling()
