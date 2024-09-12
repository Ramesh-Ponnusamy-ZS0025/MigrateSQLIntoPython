
from sqlalchemy import create_engine, func
import pandas as pd

engine = create_engine("postgresql://user:password@localhost/database")
conn = engine.connect()

def transfer(sender, receiver, amount):
    # subtracting the amount from the sender's account
    conn.execute(
        "update accounts set balance = balance - :amount where id = :sender",
        {"sender": sender, "amount": amount}
    )

    # adding the amount to the receiver's account
    conn.execute(
        "update accounts set balance = balance + :amount where id = :receiver",
        {"receiver": receiver, "amount": amount}
    )

    conn.commit()

# example usage: transfer("1234", "5678", 100)
