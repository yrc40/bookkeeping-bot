import telebot
import pandas as pd

bot = telebot.TeleBot("7204964331:AAGcJe-_-EMhYEtEIQYxkwIfkI509vC5s68")

n = 0
names = []

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello, this is bookkeeping bot!\nPlease enter the number of user:")
    bot.register_next_step_handler(message, get_num_of_people)

def get_num_of_people(message):
    global n
    if message.text.isdigit():
        n = int(message.text)
        bot.reply_to(message, 
                     f"OK, {n} people.\nPlease enter users' names in a line and sep each with comma and one space.")
        bot.register_next_step_handler(message, set_user_name)
    else: 
        bot.reply_to(message, "Invalid input.\nPlease enter number of user again.")
        bot.register_next_step_handler(message, get_num_of_people)

def set_user_name(message):
    global names
    names = message.text.split(", ")
    if len(names) != n:
        bot.reply_to(message, f"You should enter {n} names.\nPlease enter user names again.")
        bot.register_next_step_handler(message, set_user_name)
    else:
        bot.reply_to(message, f"Hi, {message.text}.\nAre the user names correct?[Y/n]")
        bot.register_next_step_handler(message, create_user_table)

def create_user_table(message):
    global names
    if message.text == 'Y':
        table = pd.DataFrame(0.0, index = names, columns = names)

        table.to_csv("user_table.csv", index = True)
        bot.reply_to(message, "create user data successfully!")
    else:
        bot.reply_to(message, "Reset user name. Please enter user names again.")
        bot.register_next_step_handler(message, set_user_name)

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

        




bot.infinity_polling()
