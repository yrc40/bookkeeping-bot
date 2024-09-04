from db import session, User, Transaction
from bot import bot
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, update

def register_user(message):
    user_id = message.from_user.id
    username = message.from_user.username
    existing_user = session.query(User).filter_by(id=user_id).first()
    
    if existing_user is None:
        user_data = User(id = user_id, name = username)
        session.add(user_data) 
        session.commit()
        bot.reply_to(message, f"Hi, @{username}. You are registered successfully.")
    else:
        bot.reply_to(message,f"User already exists: ID = {user_id}, Username = {username}")

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
                bot.send_message(message.chat.id, "Invalid receiver name. Please try again.")
        else:
            bot.send_message(message.chat.id, "Ivalid sender name. Please try again.")
    else:
        bot.send_message(message.chat.id, "Amount should greater than zero. Please try again.")

def show_bal(message):
    users = message.text.split()
    name1 = users[0].lstrip('@')
    name2 = users[1].lstrip('@')
    
    user1 = session.query(User).filter_by(name = name1).first()
    user2 = session.query(User).filter_by(name = name2).first()

    if not user1 or not user2:
        bot.reply_to(message, "Invalid user name. Please try again.")
    else: 
        sent_total = session.query(
            func.sum(Transaction.amount)).filter(
                and_(
                    Transaction.sender_id == user1.id, 
                    Transaction.receiver_id == user2.id, 
                    Transaction.chat_id == message.chat.id, 
                    Transaction.status.is_(None)
                )).scalar() or 0.0
                
        received_total = session.query(
            func.sum(Transaction.amount)).filter(
                and_(
                    Transaction.sender_id == user2.id, 
                    Transaction.receiver_id == user1.id, 
                    Transaction.chat_id == message.chat.id, 
                    Transaction.status.is_(None)
                )).scalar() or 0.0
        
        balance = sent_total - received_total

        if balance > 0:
            bot.reply_to(message, f"*--- Balance of {name1} and {name2} ---*\n{name2} should pay {name1} {abs(balance):.2f}")
        elif balance < 0:
            bot.reply_to(message, f"*--- Balance of {name1} and {name2} ---*\n{name1} should pay {name2} {abs(balance):.2f}")
        else:
            bot.reply_to(message, "Balance is even")

def transaction_record(message):
    users = message.text.split()
    name1 = users[0].lstrip('@')
    name2 = users[1].lstrip('@')
    n = int(users[2])
    user1 = session.query(User).filter_by(name = name1).first()
    user2 = session.query(User).filter_by(name = name2).first()

    if not user1 or not user2:
        bot.reply_to(message, "Invalid user name. Please try again.")
    else:
        n_days_ago = datetime.now() - timedelta(days = n)
        n_days_ago_timestamp = int(n_days_ago.timestamp())

        transactions = session.query(Transaction).filter(
            and_(
                Transaction.date >= n_days_ago_timestamp,
                or_(
                    and_(Transaction.sender_id == user1.id, Transaction.receiver_id == user2.id),
                    and_(Transaction.sender_id == user2.id, Transaction.receiver_id == user1.id)
                ), 
                Transaction.chat_id == message.chat.id, 
                Transaction.status.is_(None)
            )
        ).all()

        if not transactions:
            bot.reply_to(message, f"No transactions found between {name1} and {name2} in the past {n} days.")
        else: 
            transaction_list = []
            for transaction in transactions:
                transaction_date = datetime.fromtimestamp(transaction.date).strftime('%Y-%m-%d')
                transaction_list.append(
                    f"{transaction_date} {name1 if transaction.sender_id == user1.id else name2} -> "
                    f"{name2 if transaction.receiver_id == user2.id else name1} {transaction.amount} {transaction.memo}"
                )
            reply = "\n".join(transaction_list)
            bot.send_message(chat_id = message.chat.id, text = reply)

def mark_as_done(message):
    users = message.text.split()
    name1 = users[1].lstrip('@')
    name2 = users[2].lstrip('@')
    user1 = session.query(User).filter_by(name = name1).first()
    user2 = session.query(User).filter_by(name = name2).first()

    if not user1 or not user2:
        bot.reply_to(message, "Invalid user name. Please try again.")
    else:
        session.execute(
            update(Transaction).
            where(
                (Transaction.sender_id == user1.id) & (Transaction.receiver_id == user2.id) & (Transaction.chat_id == message.chat.id)|
                (Transaction.sender_id == user2.id) & (Transaction.receiver_id == user1.id) & (Transaction.chat_id == message.chat.id)
            ).
            values(status = 'done')
        )
        session.commit()
        bot.reply_to(message, "Delete completed!")








    
