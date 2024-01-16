import sqlite3

from flask import Flask, json, request, jsonify

app = Flask(__name__)


def create_database():
    connection = sqlite3.connect("bank.db")
    cursor = connection.cursor()
    cursor.execute(
        """ CREATE TABLE transactions (
                    transactionId INTEGER primary key,
                    accountId INTEGER,
                    isDeposit INTEGER,
                    amount REAL,
                    isSuccessful INTEGER,
                    FOREIGN KEY(accountId) REFERENCES accounts(accountId)
                    )"""
    )

    cursor.execute(
        """CREATE TABLE accounts (
                    accountId INTEGER primary key,
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
    cursor.execute("INSERT INTO transactions VALUES (0, 0, 1, 1000, 1)")
    cursor.execute("INSERT INTO transactions VALUES (1, 0, 1, 2000, 1)")
    cursor.execute("INSERT INTO transactions VALUES (2, 0, 1, 2300, 1)")
    cursor.execute("UPDATE accounts SET balance = 6300 WHERE accountId == 0")
    cursor.execute("INSERT INTO transactions VALUES (3, 1, 1, 1111, 1)")
    cursor.execute("UPDATE accounts SET balance = 2111 WHERE accountId == 1")

    connection.commit()
    connection.close()


def create_new_account(account_id):
    connection = sqlite3.connect("bank.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO accounts VALUES(?, 1000)", (account_id,))
    connection.commit()
    connection.close()


def update_database(account_id, is_deposit, amount):
    connection = sqlite3.connect("bank.db")
    cursor = connection.cursor()
    is_transaction_successful = False

    cursor.execute("SELECT * FROM accounts WHERE accountId == ?", (account_id,))
    is_account_active = len(cursor.fetchall()) > 0

    if not is_account_active:
        create_new_account(account_id)

    if is_deposit:
        cursor.execute(
            "UPDATE accounts SET balance = balance + ? WHERE accountId == ?",
            (amount, account_id),
        )
        cursor.execute(
            "INSERT INTO transactions (accountId, isDeposit, amount, isSuccessful) VALUES(?, ?, ?, ?)",
            (account_id, 1, amount, 1),
        )
        is_transaction_successful = True

    else:
        cursor.execute(
            "SELECT balance FROM accounts WHERE accountId == ?", (account_id,)
        )
        retrieved_amount = cursor.fetchall()
        if retrieved_amount[0][0] > amount:
            cursor.execute(
                "UPDATE accounts SET balance = balance - ? WHERE accountId == ?",
                (amount, account_id),
            )
            cursor.execute(
                "INSERT INTO transactions (accountId, isDeposit, amount, isSuccessful) VALUES(?, ?, ?, ?)",
                (account_id, 0, amount, 1),
            )
            is_transaction_successful = True
        else:
            cursor.execute(
                "INSERT INTO transactions (accountId, isDeposit, amount, isSuccessful) VALUES(?, ?, ?, ?)",
                (account_id, 0, amount, 0),
            )

    connection.commit()
    connection.close()
    return is_transaction_successful

def account_balance(id):
    connection = sqlite3.connect("bank.db")
    cursor = connection.cursor()
    cursor.execute("SELECT balance FROM accounts WHERE accountId == ?", (id,))
    account = cursor.fetchone()
    connection.close()
    if(account is None):
        return None
    return account[0]

def is_authorized(id):
    connection = sqlite3.connect("bank.db")
    cursor = connection.cursor()
    cursor.execute("SELECT accountId FROM accounts WHERE accountId == ?", (id,))
    account = cursor.fetchone()
    connection.close()
    return account is not None

@app.route("/bank/data/<int:account_id>", methods=["GET"])
def extract_records(account_id):
    if request.method == "GET":
        connection = sqlite3.connect("bank.db")
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * " "FROM accounts " "WHERE accountId == ?", (account_id,)
        )
        account = cursor.fetchall()

        if not account:
            connection.close()
            return json.dumps({"error": "Account not found"}), 404

        cursor.execute(
            "SELECT * " "FROM transactions " "WHERE accountId == ?", (account_id,)
        )
        transactions_records = cursor.fetchall()

        connection.close()

        account_dict = {"idKonta": account[0][0], "bilans": account[0][1]}

        transactions = [
            {
                "idTransakcji": record[0],
                "idKonta": record[1],
                "czyWplata": bool(record[2]),
                "wartoscTransakcji": record[3],
                "czyUdana": record[4],
            }
            for record in transactions_records
        ]

        response = jsonify({"account": account_dict, "transactions": transactions})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response


if __name__ == "__main__":
    # create_database()
    # insert_test_records()
    # print(update_database(0, True, 1000))
    # print(update_database(0, False, 5300))
    # print(update_database(0, False, 1000))
    # print(update_database(1, False, 20000))
    # print(update_database(2, True, 1000000))
    app.run(debug=True)
