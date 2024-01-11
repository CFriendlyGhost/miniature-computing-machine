import sqlite3

from engineio import json


def create_database():
    connection = sqlite3.connect("bank.db")
    cursor = connection.cursor()
    cursor.execute(
        """ CREATE TABLE transactions (
                    transaction_id INTEGER primary key,
                    account_id INTEGER,
                    isDeposit INTEGER,
                    amount REAL,
                    FOREIGN KEY(account_id) REFERENCES accounts(account_id)
                    )"""
    )

    cursor.execute(
        """CREATE TABLE accounts (
                    account_id INTEGER primary key,
                    balance REAL
                    )"""
    )
    connection.commit()
    connection.close()


def insert_test_records():
    connection = sqlite3.connect("bank.db")
    cursor = connection.cursor()

    cursor.execute("INSERT INTO accounts VALUES(0, 1000)")
    cursor.execute("INSERT INTO accounts VALUES (1, 1000)")
    cursor.execute("INSERT INTO transactions VALUES (0, 0, 300, 0)")
    cursor.execute("INSERT INTO transactions VALUES (1, 1, 350, 1)")

    connection.commit()
    connection.close()


def extract_records():
    connection = sqlite3.connect("bank.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM accounts")
    accounts_records = cursor.fetchall()

    cursor.execute("SELECT * FROM transactions")
    transactions_records = cursor.fetchall()

    connection.close()

    accounts = [
        {"idKonta": record[0], "bilans": record[1]} for record in accounts_records
    ]
    transactions = [
        {
            "idTransakcji": record[0],
            "idKonta": record[1],
            "czyWplata": bool(record[2]),
            "stanKonta": record[3],
        }
        for record in transactions_records
    ]

    return json.dumps({"accounts": accounts, "transactions": transactions})


if __name__ == "__main__":
    create_database()
    insert_test_records()
    print(json.loads(extract_records()))
