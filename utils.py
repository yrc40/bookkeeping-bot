from db import session, User, Transaction
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, update


def register_user(message):
    user_id = message.from_user.id
    username = message.from_user.username
    existing_user = session.query(User).filter_by(id=user_id).first()

    if existing_user is None:
        user_data = User(id=user_id, name=username)
        session.add(user_data)
        session.commit()
        return f"Hi, @{username}. You are registered successfully."
    else:
        return f"User already exists: ID = {user_id}, Username = {username}"


def transaction_process(message):
    trans = message.text.split()
    if len(trans) < 4:
        return "Invalid input. Please try again."
    else:
        sender = trans[1].lstrip("@")
        receiver = trans[2].lstrip("@")
        amount = float(trans[3])
    if len(trans) > 4:
        memo = trans[4]
    else:
        memo = ""
        
    if amount > 0:
        if session.query(User).filter_by(name=sender).first() is not None:
            if session.query(User).filter_by(name=receiver).first() is not None:
                senderID = session.query(User).filter_by(name=sender).first().id
                reveiverID = session.query(User).filter_by(name=receiver).first().id
                transaction = Transaction(
                    chat_id=message.chat.id,
                    date=message.date,
                    sender_id=senderID,
                    receiver_id=reveiverID,
                    amount=amount,
                    memo=memo,
                )
                session.add(transaction)
                session.commit()
                return "Transaction added successfully!"
            else:
                return "Invalid receiver name. Please try again."
        else:
            return "Ivalid sender name. Please try again."
    else:
        return "Amount should greater than zero. Please try again."


def show_bal(message):
    users = message.text.split()
    if len(users) != 3:
        return "Invalid input. Please try again."
    else:
        name1 = users[1].lstrip("@")
        name2 = users[2].lstrip("@")

    user1 = session.query(User).filter_by(name=name1).first()
    user2 = session.query(User).filter_by(name=name2).first()

    if not user1 or not user2:
        return "Invalid user name. Please try again."
    else:
        sent_total = (
            session.query(func.sum(Transaction.amount))
            .filter(
                and_(
                    Transaction.sender_id == user1.id,
                    Transaction.receiver_id == user2.id,
                    Transaction.chat_id == message.chat.id,
                    Transaction.status.is_(None),
                )
            )
            .scalar()
            or 0.0
        )

        received_total = (
            session.query(func.sum(Transaction.amount))
            .filter(
                and_(
                    Transaction.sender_id == user2.id,
                    Transaction.receiver_id == user1.id,
                    Transaction.chat_id == message.chat.id,
                    Transaction.status.is_(None),
                )
            )
            .scalar()
            or 0.0
        )

        balance = sent_total - received_total

        if balance > 0:
            return f"*--- Balance of {name1} and {name2} ---*\n{name2} should pay {name1} {abs(balance):.2f}"
        elif balance < 0:
            return f"*--- Balance of {name1} and {name2} ---*\n{name1} should pay {name2} {abs(balance):.2f}"
        else:
            return "Balance is even"


def transaction_record(message):
    users = message.text.split()
    if len(users) != 4:
        return "Invalid input. Please try again."
    else:
        name1 = users[1].lstrip("@")
        name2 = users[2].lstrip("@")
        n = int(users[3])

    user1 = session.query(User).filter_by(name=name1).first()
    user2 = session.query(User).filter_by(name=name2).first()

    if not user1 or not user2:
        return "Invalid user name. Please try again."
    else:
        n_days_ago = datetime.now() - timedelta(days=n)
        n_days_ago_timestamp = int(n_days_ago.timestamp())

        transactions = (
            session.query(Transaction)
            .filter(
                and_(
                    Transaction.date >= n_days_ago_timestamp,
                    or_(
                        and_(
                            Transaction.sender_id == user1.id,
                            Transaction.receiver_id == user2.id,
                        ),
                        and_(
                            Transaction.sender_id == user2.id,
                            Transaction.receiver_id == user1.id,
                        ),
                    ),
                    Transaction.chat_id == message.chat.id,
                    Transaction.status.is_(None),
                )
            )
            .all()
        )

        if not transactions:
            return f"No transactions found between {name1} and {name2} in the past {n} days."
        else:
            transaction_list = []
            for transaction in transactions:
                transaction_date = datetime.fromtimestamp(transaction.date).strftime(
                    "%Y-%m-%d"
                )
                transaction_list.append(
                    f"{transaction_date} {name1 if transaction.sender_id == user1.id else name2} -> "
                    f"{name2 if transaction.receiver_id == user2.id else name1} {transaction.amount} {transaction.memo}"
                )
            return "\n".join(transaction_list)


def mark_as_done(message):
    users = message.text.split()
    if len(users) != 3:
        return "Invalid input. Please try again."
    else:
        name1 = users[1].lstrip("@")
        name2 = users[2].lstrip("@")
        
    user1 = session.query(User).filter_by(name=name1).first()
    user2 = session.query(User).filter_by(name=name2).first()

    if not user1 or not user2:
        return "Invalid user name. Please try again."
    else:
        session.execute(
            update(Transaction)
            .where(
                (Transaction.sender_id == user1.id)
                & (Transaction.receiver_id == user2.id)
                & (Transaction.chat_id == message.chat.id)
                | (Transaction.sender_id == user2.id)
                & (Transaction.receiver_id == user1.id)
                & (Transaction.chat_id == message.chat.id)
            )
            .values(status="done")
        )
        session.commit()
        return "Delete completed!"
