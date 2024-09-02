from db import session, User, Transaction
from bot import bot

def transaction_process(message):
    trans = message.text.split()
    sender = trans[0].lstrip('@')
    receiver = trans[1].lstrip('@')
    amount = float(trans[2])
    if len(trans) > 3:
        memo = trans[3]
    else: 
        memo = ""
    if amount > 0:
        if session.query(User).filter_by(name = sender).first() is not None:
            if session.query(User).filter_by(name = receiver).first() is not None:
                senderID = session.query(User).filter_by(name = sender).first().id
                reveiverID = session.query(User).filter_by(name = receiver).first().id
                transaction = Transaction(chat_id = message.chat.id, date = message.date, sender_id = senderID, receiver_id = reveiverID, amount = amount, memo = memo)
                session.add(transaction) 
                session.commit()
                bot.send_message(message.chat.id, "Transaction added successfully!")
            else:
                reply = "Ivalid receiver name. Please try again"
        #bot.register_next_step_handler(message, enter_transaction)
    #else:
        #table = pd.read_csv("user_table.csv", index_col = 0)
        #if sender in table.index and receiver in table.columns:
            #table.at[sender, receiver] += amount
            #table.to_csv("user_table.csv", index = True)
            #bot.reply_to(message, f"Transaction of {amount} from {sender} to {receiver} recorded.")
        #else:
            #bot.reply_to(message, "Invalid sender or receiver. Please enter the transaction again.")
            #bot.register_next_step_handler(message, enter_transaction)
